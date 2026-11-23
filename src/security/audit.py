"""Trilha de auditoria do assistente (logs/audit.jsonl).

Cada interação registra: timestamp, usuário, pergunta, provedor, paciente
consultado, exames/alertas consultados, urgência, fontes citadas, alerta
emitido, guardrails aplicados e resposta final (P007).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class AuditTrail:
    def __init__(self, log_dir: Path):
        self.path = log_dir / "audit.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def registrar(self, entrada: dict) -> None:
        registro = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            **entrada,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
