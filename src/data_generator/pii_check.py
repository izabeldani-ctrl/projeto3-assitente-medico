"""Verificação de anonimização/PII do dataset e do banco sintético.

Checa:
- Padrões de CPF, e-mail e telefone em qualquer texto;
- Menção a instituições de saúde reais (blacklist);
- Nomes do banco restritos ao pool de nomes fictícios;
- Aderência dos códigos de protocolo citados no dataset (curadoria).
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

RE_CPF = re.compile(r"\d{3}[.\-]?\d{3}[.\-]?\d{3}[.\-]?\d{2}")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
RE_PHONE = re.compile(r"\(?\d{2}\)?\s?\d{4,5}-\d{4}")

INSTITUTION_BLACKLIST = [
    "sírio", "sirio", "einstein", "albert einstein", "hcor", "usp",
    "unicamp", "fiocruz", "samaritano", "9 de julho", "beneficência",
    "beneficencia", "santa casa", "cruz vermelha",
]

RE_PROTOCOL = re.compile(r"\bP0(0[1-7])\b")


def _scan_text(text: str, where: str, issues: list[str]):
    lowered = text.lower()
    if RE_CPF.search(text):
        issues.append(f"{where}: padrão de CPF encontrado.")
    if RE_EMAIL.search(text):
        issues.append(f"{where}: padrão de e-mail encontrado.")
    if RE_PHONE.search(text):
        issues.append(f"{where}: padrão de telefone encontrado.")
    for inst in INSTITUTION_BLACKLIST:
        if re.search(rf"(?<!\w){re.escape(inst)}(?!\w)", lowered):
            issues.append(f"{where}: menção a instituição real ('{inst}').")


def _protocolos_citados(text: str) -> set[str]:
    return {f"P0{m}" for m in RE_PROTOCOL.findall(text)}


def check_dataset(jsonl_paths: list[Path]) -> tuple[list[str], dict]:
    issues: list[str] = []
    n_samples = 0
    cited: set[str] = set()
    for path in jsonl_paths:
        with path.open(encoding="utf-8") as f:
            for line in f:
                n_samples += 1
                sample = json.loads(line)
                for msg in sample["messages"]:
                    _scan_text(msg["content"], f"{path.name}:{msg['role']}", issues)
                    cited |= _protocolos_citados(msg["content"])
    valid_codes = {f"P{i:03d}" for i in range(1, 8)}
    unknown = cited - valid_codes
    if unknown:
        issues.append(f"dataset cita códigos de protocolo inexistentes: {sorted(unknown)}")
    return issues, {"n_samples": n_samples, "protocolos_citados": sorted(cited)}


def check_db(db_path: Path, name_pool: tuple[set[str], set[str]]) -> list[str]:
    issues: list[str] = []
    first_names, last_names = name_pool
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT nome FROM pacientes").fetchall()
    for (nome,) in rows:
        parts = nome.split()
        if not parts or parts[0] not in first_names or parts[-1] not in last_names:
            issues.append(f"hospital.db: nome fora do pool fictício — '{nome}'")
    for table, col in (("exames", "resultado"), ("alertas", "mensagem")):
        for (msg,) in conn.execute(f"SELECT {col} FROM {table} WHERE {col} IS NOT NULL"):
            _scan_text(str(msg), f"hospital.db:{table}", issues)
    conn.close()
    return issues


def run_all(data_dir: Path) -> bool:
    from .names import FICTIONAL_FIRST_NAMES, FICTIONAL_LAST_NAMES

    fine_tune_dir = data_dir / "fine_tune"
    db_path = data_dir / "hospital.db"

    issues, info = check_dataset(sorted(fine_tune_dir.glob("*.jsonl")))
    issues += check_db(db_path, (set(FICTIONAL_FIRST_NAMES), set(FICTIONAL_LAST_NAMES)))

    print("=" * 60)
    print("Verificação de anonimização/PII — dados sintéticos do HospitalTech")
    print("=" * 60)
    print(f"Amostras analisadas: {info['n_samples']}")
    print(f"Protocolos citados:   {', '.join(info['protocolos_citados'])}")
    if issues:
        print(f"\n[FALHOU] {len(issues)} problema(s):")
        for i in issues:
            print(f"  - {i}")
        return False
    print("\n[OK] Nenhum padrão de PII, instituição real ou nome fora do pool.")
    print("[OK] Códigos de protocolo citados existem (P001–P007).")
    return True
