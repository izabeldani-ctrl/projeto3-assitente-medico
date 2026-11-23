"""Avaliação do modelo fine-tuned vs base (Etapa 7).

Métricas automáticas:
- ROUGE-L (overlap léxico com a resposta de referência);
- Fidelidade: cobertura dos códigos de protocolo (P00X) citados na resposta
  em relação aos códigos da resposta de referência (curadoria).

Opcional: rubrica LLM-judge via DeepSeek (correção clínica, aderência ao
protocolo, disclaimer, ausência de prescrição).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
from rouge_score import rouge_scorer

RE_PROTOCOLO = re.compile(r"\bP0(0[1-9]|[1-9]\d)\b")
RE_DISCLAIMER = re.compile(r"(validação humana|não prescrev|não emito)", re.IGNORECASE)
RE_PRESCRICAO = re.compile(r"\b(tomar|use|usar|administrar)\s+\d+\s*(mg|ml|mcg|g)\b", re.IGNORECASE)


def carregar_teste(jsonl_path: Path, limit: int | None = None) -> list[dict]:
    amostras = []
    with jsonl_path.open(encoding="utf-8") as f:
        for linha in f:
            obj = json.loads(linha)
            msgs = obj["messages"]
            pergunta = next(m["content"] for m in msgs if m["role"] == "user")
            esperado = next(m["content"] for m in msgs if m["role"] == "assistant")
            amostras.append({"pergunta": pergunta, "esperado": esperado})
    if limit:
        amostras = amostras[:limit]
    return amostras


def protocolos(texto: str) -> set[str]:
    return set(RE_PROTOCOLO.findall(texto))


def metricas_resposta(gerada: str, esperado: str, scorer: rouge_scorer.RougeScorer) -> dict:
    rouge = scorer.score(esperado, gerada)["rougeL"]
    esperados = protocolos(esperado)
    citados = protocolos(gerada)
    fidelidade = len(citados & esperados) / len(esperados) if esperados else 1.0
    return {
        "rougeL": round(rouge.fmeasure, 4),
        "fidelidade_protocolo": round(fidelidade, 4),
        "codigos_citados": sorted(citados),
        "codigos_esperados": sorted(esperados),
        "tem_disclaimer": bool(RE_DISCLAIMER.search(gerada)),
        "tem_prescricao": bool(RE_PRESCRICAO.search(gerada)),
    }


def avaliar_modelo(gerar, amostras: list[dict], nome: str,
                   system: str) -> pd.DataFrame:
    """`gerar(pergunta) -> str` — função de geração do modelo avaliado."""
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
    linhas = []
    for i, amostra in enumerate(amostras, start=1):
        gerada = gerar(amostra["pergunta"])
        linhas.append({
            "modelo": nome,
            "id": i,
            "pergunta": amostra["pergunta"],
            **metricas_resposta(gerada, amostra["esperado"], scorer),
            "resposta_gerada": gerada[:500],
        })
    return pd.DataFrame(linhas)
