"""Fluxo do assistente médico com LangGraph (Etapa 4).

Grafo de estados:

    START → identificar_paciente → verificar_exames → classificar_urgencia
          → recuperar_protocolos → responder → emitir_alertas → END

Cada nó é determinístico exceto ``identificar_paciente`` e ``responder``,
que chamam a LLM configurada (provider ollama|deepseek).
"""

from __future__ import annotations

import json
import re
from functools import partial
from typing import Any, Callable, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from ..security.guardrails import checar_entrada, validar_saida
from ..security.logging_utils import get_logger
from . import db
from .config import SYSTEM_PROMPT
from .protocols_kb import ProtocolosKB

logger = get_logger("hospitaltech.assistant")


class Estado(TypedDict, total=False):
    pergunta: str
    provedor: str
    paciente_id: int | None
    prontuario: dict
    urgencia: str
    fontes: list[str]
    contexto_protocolos: str
    resposta: str
    alerta: str | None
    avisos: list[str]
    bloqueada: str | None


# --------------------------------------------------------------------------
# Nós do grafo
# --------------------------------------------------------------------------

def _conteudo(resposta) -> str:
    return resposta.content if hasattr(resposta, "content") else str(resposta)


def _extrair_paciente_llm(pergunta: str, llm) -> int | None:
    prompt = [
        SystemMessage(
            "Você extrai dados de mensagens clínicas. Responda APENAS com JSON "
            'válido no formato {"paciente_id": <int ou null>}. Se a mensagem '
            'mencionar um nome sem id, use {"paciente_id": null, "nome": "<nome>"}.'
        ),
        HumanMessage(f"Mensagem: {pergunta}"),
    ]
    texto = _conteudo(llm.invoke(prompt)).strip()
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError:
        m = re.search(r'"paciente_id"\s*:\s*(\d+)', texto)
        dados = {"paciente_id": int(m.group(1)) if m else None}
        m_nome = re.search(r'"nome"\s*:\s*"([^"]+)"', texto)
        if m_nome:
            dados["nome"] = m_nome.group(1)
    if not dados.get("paciente_id") and dados.get("nome"):
        matches = db.buscar_pacientes_por_nome(dados["nome"])
        if matches:
            dados["paciente_id"] = matches[0]["id"]
    return dados.get("paciente_id")


def identificar_paciente(estado: Estado, llm) -> Estado:
    if estado.get("paciente_id") is not None:
        return estado
    try:
        estado["paciente_id"] = _extrair_paciente_llm(estado["pergunta"], llm)
    except Exception as exc:  # LLM indisponível não derruba o fluxo
        logger.warning("identificação de paciente indisponível: %s", exc)
        estado["paciente_id"] = None
    logger.info("paciente identificado: %s", estado["paciente_id"])
    return estado


def verificar_exames(estado: Estado) -> Estado:
    pid = estado.get("paciente_id")
    if pid is None:
        estado["prontuario"] = {}
        logger.info("sem paciente associado — modo FAQ/protocolo")
        return estado
    estado["prontuario"] = db.resumo_prontuario(pid)
    exames = estado["prontuario"].get("exames", [])
    logger.info(
        "prontuário consultado: paciente=%s exames=%d alertas=%d",
        pid, len(exames), len(estado["prontuario"].get("alertas", [])),
    )
    return estado


def classificar_urgencia(estado: Estado) -> Estado:
    prontuario = estado.get("prontuario") or {}
    if not prontuario or "erro" in prontuario:
        estado["urgencia"] = "sem alerta"
        return estado
    texto = json.dumps(prontuario, ensure_ascii=False).lower()
    criticos = ("bi-rads 5", "positivo para malignidade", "supradesnivelamento")
    if any(k in texto for k in criticos):
        urgencia = "critico"
    elif "atrasado" in texto or "bi-rads 4c" in texto:
        urgencia = "urgente"
    elif "pendente" in texto:
        urgencia = "informativo"
    else:
        urgencia = "sem alerta"
    estado["urgencia"] = urgencia
    logger.info("classificação de urgência: %s", urgencia)
    return estado


def recuperar_protocolos(estado: Estado, kb: ProtocolosKB) -> Estado:
    trechos = kb.buscar(estado["pergunta"], k=3)
    estado["fontes"] = [t.rotulo for t in trechos]
    estado["contexto_protocolos"] = "\n\n".join(
        f"[{t.rotulo}]\n{t.texto[:900]}" for t in trechos
    )
    logger.info("protocolos recuperados: %s", estado["fontes"])
    return estado


def gerar_resposta(estado: Estado, llm) -> Estado:
    prontuario_json = json.dumps(
        estado.get("prontuario") or {}, ensure_ascii=False, indent=2
    )
    contexto = estado.get("contexto_protocolos") or "Nenhum protocolo recuperado."
    system = (
        SYSTEM_PROMPT
        + "\n\n## Contexto do paciente (prontuário sintético)\n"
        + prontuario_json
        + "\n\n## Trechos de protocolos recuperados\n"
        + contexto
        + "\n\nRegras de resposta: cite o código P00X de cada protocolo usado; "
          "indique a fonte consultada; jamais prescreva ou emita alta (P007); "
          "se não houver paciente no contexto, responda com base apenas nos "
          "protocolos internos."
    )
    resposta = llm.invoke([SystemMessage(system), HumanMessage(estado["pergunta"])])
    estado["resposta"] = _conteudo(resposta)
    return estado


def emitir_alertas(estado: Estado) -> Estado:
    urgencia = estado.get("urgencia", "sem alerta")
    pid = estado.get("paciente_id")
    if urgencia == "critico":
        estado["alerta"] = (
            f"ALERTA CRÍTICO emitido (P006) para o paciente {pid}: acionamento "
            "imediato do plantão médico, com confirmação de recebimento obrigatória."
        )
    elif urgencia == "urgente":
        estado["alerta"] = (
            f"ALERTA URGENTE emitido (P006) para o paciente {pid}: notificação ao "
            "solicitante e à coordenação para revisão das pendências."
        )
    elif urgencia == "informativo":
        estado["alerta"] = (
            f"Alerta informativo registrado (P006) para o paciente {pid}: exibição "
            "no painel eletrônico do solicitante."
        )
    else:
        estado["alerta"] = None
    if estado["alerta"]:
        logger.warning(estado["alerta"])
    return estado


# --------------------------------------------------------------------------
# Construção e execução
# --------------------------------------------------------------------------

def criar_grafo(llm, kb: ProtocolosKB | None = None) -> StateGraph:
    kb = kb or ProtocolosKB()
    grafo = StateGraph(Estado)
    grafo.add_node("identificar_paciente", partial(identificar_paciente, llm=llm))
    grafo.add_node("verificar_exames", verificar_exames)
    grafo.add_node("classificar_urgencia", classificar_urgencia)
    grafo.add_node("recuperar_protocolos", partial(recuperar_protocolos, kb=kb))
    grafo.add_node("responder", partial(gerar_resposta, llm=llm))
    grafo.add_node("emitir_alertas", emitir_alertas)

    grafo.add_edge(START, "identificar_paciente")
    grafo.add_edge("identificar_paciente", "verificar_exames")
    grafo.add_edge("verificar_exames", "classificar_urgencia")
    grafo.add_edge("classificar_urgencia", "recuperar_protocolos")
    grafo.add_edge("recuperar_protocolos", "responder")
    grafo.add_edge("responder", "emitir_alertas")
    grafo.add_edge("emitir_alertas", END)
    return grafo.compile()


def executar(grafo, pergunta: str, provedor: str, paciente_id: int | None = None,
             segunda_opiniao_llm=None) -> dict:
    """Executa o fluxo completo com guardrails de entrada e saída."""
    bloqueio = checar_entrada(pergunta)
    if bloqueio:
        return {
            "pergunta": pergunta,
            "provedor": provedor,
            "bloqueada": bloqueio,
            "resposta": bloqueio,
            "paciente_id": None,
            "urgencia": "sem alerta",
            "fontes": ["P007"],
            "alerta": None,
            "avisos": ["entrada bloqueada pelo guardrail (P007)"],
        }

    final: dict = grafo.invoke(
        {"pergunta": pergunta, "provedor": provedor, "paciente_id": paciente_id}
    )

    usou_contexto = bool(final.get("fontes") or (final.get("prontuario") or {}).get("exames"))
    checagem = validar_saida(final.get("resposta", ""), usou_contexto)
    final["resposta"] = checagem["texto"]
    final["avisos"] = checagem["avisos"]

    if segunda_opiniao_llm is not None:
        try:
            opiniao = gerar_resposta(dict(final), segunda_opiniao_llm)
            checagem2 = validar_saida(opiniao["resposta"], usou_contexto)
            final["segunda_opiniao"] = checagem2["texto"]
            final["segunda_opiniao_provedor"] = "deepseek"
        except Exception as exc:
            logger.error("segunda opinião indisponível: %s", exc)
            final["segunda_opiniao"] = f"[segunda opinião indisponível: {exc}]"

    return final
