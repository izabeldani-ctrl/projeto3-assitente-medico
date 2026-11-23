"""Guardrails do assistente (P007).

1. Guardrail de entrada: bloqueia temas fora do escopo com mensagem padrão.
2. Guardrail de saída: verifica a resposta gerada quanto a:
   - linguagem de prescrição/alta/diagnóstico definitivo (proibidos);
   - presença de disclaimer de validação humana (obrigatório em conteúdo clínico);
   - citação de fonte (código P00X) quando a resposta menciona protocolo/conduta.
"""

from __future__ import annotations

import re

DISCLAIMER_PADRAO = (
    "\n\n⚠️ Resposta gerada pelo assistente institucional — "
    "validação humana obrigatória (P007)."
)

# Temas claramente fora do escopo do assistente institucional (P007)
FORA_DE_ESCOPO: list[tuple[str, str]] = [
    (r"\b(receita de bolo|programa[cç][aã]o em|python|javascript)\b",
     "assuntos não clínicos"),
    (r"\b(futebol|pol[ií]tica|elei[cç][oõ]es|clima|previs[aã]o do tempo)\b",
     "assuntos gerais"),
    (r"\b(jur[ií]dico|advogado|processo judicial)\b",
     "assuntos jurídicos"),
]

# Padrões de linguagem proibida nas respostas (P007)
PADROES_PRESCRICAO = [
    re.compile(r"prescrev[oa]\w*\s+[a-z]", re.IGNORECASE),
    re.compile(r"\b(tomar|use|usar|administrar)\s+\d+\s*(mg|ml|mcg|g)\b", re.IGNORECASE),
    re.compile(r"\b\d+\s*(mg|ml|mcg)\b.*\b(por|ao)\s+dia\b", re.IGNORECASE),
    re.compile(r"\bde\s+alta\b.*\b(paciente|hospitalar)\b", re.IGNORECASE),
    re.compile(r"diagn[oó]stico\s+definitivo", re.IGNORECASE),
]

# Termos que negam a linguagem proibida em uma janela curta antes do match
NEGACOES = ("não", "nao", "nunca", "jamais", "nem")


def _negado(texto: str, inicio: int) -> bool:
    """Verifica se o trecho proibido está em contexto negado."""
    janela = texto[max(0, inicio - 40):inicio].lower()
    return any(neg in janela for neg in NEGACOES)

RE_PROTOCOLO = re.compile(r"\bP0(0[1-9]|[1-9]\d)\b")
RE_CONTEXTO_CLINICO = re.compile(
    r"\b(BI-RADS|bi[oó]psia|exame|protocolo|conduta|mamografia|"
    r"dor tor[aá]cica|alerta|oncolog|laudo|rastreamento)\b",
    re.IGNORECASE,
)


def checar_entrada(pergunta: str) -> str | None:
    """Retorna mensagem de bloqueio, ou None se a pergunta está liberada."""
    for pattern, tema in FORA_DE_ESCOPO:
        if re.search(pattern, pergunta, re.IGNORECASE):
            return (
                f"Este tema ({tema}) está fora do escopo dos protocolos internos "
                "do HospitalTech. Conforme a P007, oriento buscar o canal adequado "
                "e não respondo clinicamente fora do escopo."
            )
    return None


def validar_saida(resposta: str, usou_contexto_clinico: bool) -> dict:
    """Valida a resposta gerada e aplica correções automáticas.

    Retorna: {"ok": bool, "avisos": [str], "texto": str (final)}
    """
    avisos: list[str] = []
    texto = resposta.strip()

    # 1) Linguagem proibida (prescrição/alta/diagnóstico) — ignora contexto negado
    for pattern in PADROES_PRESCRICAO:
        m = pattern.search(texto)
        if m and not _negado(texto, m.start()):
            avisos.append("padrão de linguagem proibida detectado (P007)")
            texto = (
                texto
                + "\n\n⚠️ Correção automática (P007): o assistente não prescreve, "
                  "não emite alta e não firma diagnóstico definitivo."
            )
            break

    # 2) Citação de fonte quando há conteúdo clínico
    tem_clinico = usou_contexto_clinico or bool(RE_CONTEXTO_CLINICO.search(texto))
    if tem_clinico and not RE_PROTOCOLO.search(texto):
        avisos.append("resposta clínica sem citação de protocolo (P00X)")
        texto += "\n\n📎 Fonte: validar conduta nos protocolos internos do HospitalTech (P001–P007)."

    # 3) Disclaimer obrigatório (a menção ao código P007 não substitui a frase)
    if "validação humana" not in texto.lower():
        texto += DISCLAIMER_PADRAO

    return {"ok": not avisos, "avisos": avisos, "texto": texto}
