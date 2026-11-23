"""Constrói o dataset instruction-style (chat template do Llama 3.2) com
variação determinística (seed fixa).

Formato de cada linha (JSONL):
    {"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from .faqs import FAQ_ENTRIES, REFUSAL_ENTRIES
from .protocols_data import PROTOCOLS
from .templates import (
    CONTEXT_PREFIXES,
    IDADES,
    FLUXO_TEMPLATES,
    LAUDO_CASES,
    LAUDO_QUESTION_FORMS,
    SOLICITACAO_TEMPLATES,
    laudo_answer,
)

SYSTEM_PROMPT = (
    "Você é o Assistente Médico Virtual do HospitalTech, treinado com os "
    "protocolos internos do hospital. Você responde dúvidas de médicos e da "
    "enfermagem, estrutura laudos e fluxos conforme os protocolos internos e "
    "sugere condutas padronizadas. Limites de atuação (P007): nunca prescreva "
    "medicamentos, nunca emita alta, nunca firme diagnóstico definitivo e "
    "sempre indique validação humana. Cite o código do protocolo utilizado "
    "(ex.: P001). Responda em português do Brasil."
)

SECTION_QUESTION_FORMS = [
    "O que o protocolo {code} estabelece sobre {heading}?",
    "Qual a orientação do {code} para {heading}?",
    "Resuma o que diz o {code} sobre {heading}.",
    "Segundo o {code}, o que é definido em {heading}?",
]


def chat_sample(user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


def _prefix(rng: random.Random, index: int) -> str:
    prefix = CONTEXT_PREFIXES[index % len(CONTEXT_PREFIXES)]
    idade = IDADES[index % len(IDADES)]
    return prefix.format(idade=idade)


def _first_sentences(text: str, n: int = 2) -> str:
    parts = text.replace("\n", " ").split(". ")
    return ". ".join(parts[:n]).rstrip(".") + "."


def build_samples(seed: int = 42) -> tuple[list[dict], dict]:
    rng = random.Random(seed)
    samples: list[dict] = []
    stats: dict[str, int] = {}

    # 1) FAQ de médicos (com prefixos de contexto)
    for entry in FAQ_ENTRIES:
        for qi, q in enumerate(entry["questions"]):
            for ai, a in enumerate(entry["answers"]):
                for pi in range(4):
                    idx = qi * 12 + ai * 4 + pi
                    q_final = (_prefix(rng, idx) + q).strip()
                    samples.append(chat_sample(q_final, a))
    stats["faq"] = len(samples)

    # 2) Seções dos protocolos
    for proto in PROTOCOLS:
        for section in proto["sections"]:
            for form in SECTION_QUESTION_FORMS:
                q = form.format(code=proto["code"], heading=section["heading"])
                a = (
                    f"Conforme o protocolo {proto['code']} ({proto['title']}), "
                    f"seção '{section['heading']}': "
                    f"{_first_sentences(section['body'])} Fonte: {proto['code']}."
                )
                samples.append(chat_sample(q, a))
    stats["protocolo"] = len(samples) - stats["faq"]

    # 3) Laudos
    before = len(samples)
    for exame, cases in LAUDO_CASES.items():
        for case_idx, (achado, birads, rec) in enumerate(cases):
            for idade in (IDADES[case_idx % len(IDADES)], IDADES[(case_idx + 3) % len(IDADES)]):
                for form in LAUDO_QUESTION_FORMS:
                    q = form.format(exame=exame, idade=idade, achado=achado)
                    samples.append(chat_sample(q, laudo_answer(exame, idade, achado, birads, rec)))
    stats["laudo"] = len(samples) - before

    # 4) Solicitações de procedimentos (sem prescrição)
    before = len(samples)
    for tpl in SOLICITACAO_TEMPLATES:
        for q in tpl["questions"]:
            for a in tpl["answers"]:
                samples.append(chat_sample(q, a))
    stats["solicitacao"] = len(samples) - before

    # 5) Fluxos automatizados
    before = len(samples)
    for tpl in FLUXO_TEMPLATES:
        for qi, q in enumerate(tpl["questions"]):
            for ai, a in enumerate(tpl["answers"]):
                for pi in range(3):
                    idx = qi * 6 + ai * 3 + pi
                    q_final = (_prefix(rng, idx) + q).strip()
                    samples.append(chat_sample(q_final, a))
    stats["fluxo"] = len(samples) - before

    # 6) Recusas (reforço do P007)
    before = len(samples)
    for entry in REFUSAL_ENTRIES:
        for q in entry["questions"]:
            for a in entry["answers"]:
                samples.append(chat_sample(q, a))
    stats["recusa"] = len(samples) - before

    rng.shuffle(samples)

    # Deduplicação por (pergunta, resposta)
    seen: set[tuple[str, str]] = set()
    unique = []
    for s in samples:
        key = (s["messages"][1]["content"], s["messages"][2]["content"])
        if key not in seen:
            seen.add(key)
            unique.append(s)
    stats["total_gerado"] = len(samples)
    stats["total_unico"] = len(unique)
    return unique, stats


def write_splits(samples: list[dict], out_dir: Path, seed: int = 42) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    rng.shuffle(samples)
    n = len(samples)
    n_train = round(n * 0.8)
    n_val = round(n * 0.1)
    splits = {
        "train": samples[:n_train],
        "val": samples[n_train : n_train + n_val],
        "test": samples[n_train + n_val :],
    }
    for name, part in splits.items():
        path = out_dir / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for sample in part:
                f.write(json.dumps(sample, ensure_ascii=False) + "\n")
    return {k: len(v) for k, v in splits.items()}
