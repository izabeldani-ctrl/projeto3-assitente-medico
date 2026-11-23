"""Tools LangChain sobre a base estruturada (prontuários) e os protocolos.

As consultas são somente-leitura (conexão ``mode=ro``) e retornam JSON
compacto — usáveis por qualquer agente LangChain.
"""

from __future__ import annotations

from langchain_core.tools import tool

from . import db
from .protocols_kb import ProtocolosKB

_kb = ProtocolosKB()


@tool
def consultar_paciente(paciente_id: int) -> str:
    """Busca dados cadastrais de um paciente pelo id."""
    return _json(db.get_paciente(paciente_id))


@tool
def consultar_exames_paciente(paciente_id: int) -> str:
    """Lista os exames de um paciente (status, datas e resultados)."""
    return _json(db.listar_exames(paciente_id))


@tool
def consultar_alertas_paciente(paciente_id: int) -> str:
    """Lista os alertas emitidos para um paciente."""
    return _json(db.listar_alertas(paciente_id))


@tool
def consultar_protocolo(consulta: str) -> str:
    """Recupera trechos relevantes dos protocolos internos (P001–P007)."""
    trechos = _kb.buscar(consulta, k=3)
    if not trechos:
        return "Nenhum trecho relevante encontrado nos protocolos internos."
    return _json([{"fonte": t.rotulo, "trecho": t.texto[:600]} for t in trechos])


def _json(obj) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False, indent=2)


FERRAMENTAS = [
    consultar_paciente,
    consultar_exames_paciente,
    consultar_alertas_paciente,
    consultar_protocolo,
]
