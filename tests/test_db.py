"""Testes da camada de dados (prontuários somente-leitura)."""

from __future__ import annotations

import sqlite3

import pytest

from src.assistant import db


def test_get_paciente_existente():
    paciente = db.get_paciente(1)
    assert paciente is not None
    assert set(paciente) >= {"id", "nome", "idade", "sexo"}
    assert paciente["id"] == 1


def test_get_paciente_inexistente():
    assert db.get_paciente(99999) is None


def test_listar_exames_paciente_1():
    exames = db.listar_exames(1)
    assert any(e["tipo"] == "Mamografia" and "BI-RADS 5" in (e["resultado"] or "")
               for e in exames)


def test_resumo_prontuario():
    resumo = db.resumo_prontuario(2)
    assert "erro" not in resumo
    assert resumo["paciente"]["id"] == 2
    assert {"exames", "alertas"} <= set(resumo)
    assert any(e["resultado"] == "positivo para malignidade" for e in resumo["exames"])


def test_busca_por_nome():
    paciente = db.get_paciente(1)
    primeiro_nome = paciente["nome"].split()[0]
    matches = db.buscar_pacientes_por_nome(primeiro_nome)
    assert any(m["id"] == 1 for m in matches)


def test_conexao_somente_leitura():
    with db._conn() as conn:
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("INSERT INTO pacientes (nome, idade, sexo, data_cadastro) "
                         "VALUES ('X', 1, 'x', '2026-01-01')")
