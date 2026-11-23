"""Testes da trilha de auditoria."""

from __future__ import annotations

import json

from src.security.audit import AuditTrail


def test_audit_registra_entrada(tmp_path):
    audit = AuditTrail(tmp_path / "logs")
    audit.registrar({"usuario": "medico-demo", "pergunta": "teste", "resposta": "ok"})
    linhas = (tmp_path / "logs" / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 1
    registro = json.loads(linhas[0])
    assert set(registro) >= {"timestamp", "usuario", "pergunta", "resposta"}


def test_audit_acumula_registros(tmp_path):
    audit = AuditTrail(tmp_path / "logs")
    for i in range(3):
        audit.registrar({"pergunta": f"q{i}", "resposta": "ok"})
    linhas = (tmp_path / "logs" / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 3
