"""Acesso somente-leitura aos prontuários sintéticos (SQLite).

As consultas usam conexão ``mode=ro`` (URI), garantindo que o assistente
nunca altere o banco de prontuários.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .config import DB_PATH


def _conn():
    return sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True)


def buscar_pacientes_por_nome(nome: str, limite: int = 5) -> list[dict]:
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, nome, idade, sexo FROM pacientes "
            "WHERE nome LIKE ? COLLATE NOCASE LIMIT ?",
            (f"%{nome}%", limite),
        ).fetchall()
    return [dict(r) for r in rows]


def get_paciente(paciente_id: int) -> dict | None:
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, nome, idade, sexo FROM pacientes WHERE id = ?",
            (paciente_id,),
        ).fetchone()
    return dict(row) if row else None


def listar_exames(paciente_id: int) -> list[dict]:
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT tipo, status, data_solicitacao, data_realizacao, resultado "
            "FROM exames WHERE paciente_id = ? ORDER BY data_solicitacao DESC",
            (paciente_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def listar_alertas(paciente_id: int) -> list[dict]:
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT tipo, prioridade, mensagem, criado_em FROM alertas "
            "WHERE paciente_id = ? ORDER BY criado_em DESC",
            (paciente_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def resumo_prontuario(paciente_id: int) -> dict:
    paciente = get_paciente(paciente_id)
    if paciente is None:
        return {"erro": f"paciente {paciente_id} não encontrado"}
    return {
        "paciente": paciente,
        "exames": listar_exames(paciente_id),
        "alertas": listar_alertas(paciente_id),
    }


def resumo_json(paciente_id: int) -> str:
    return json.dumps(resumo_prontuario(paciente_id), ensure_ascii=False, indent=2)
