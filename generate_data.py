"""Etapa 1 — Gera todos os dados sintéticos do HospitalTech.

Uso (a partir da raiz do projeto):
    python generate_data.py               # dataset completo (seed 42)
    python generate_data.py --limit 100   # amostra menor (testes)
    python generate_data.py --seed 7      # outra seed

Saídas:
    data/protocols/*.md      protocolos internos (P001–P007)
    data/fine_tune/*.jsonl   train / val / test (chat template Llama 3.2)
    data/hospital.db         prontuários sintéticos (SQLite)
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.data_generator.dataset_builder import build_samples, write_splits
from src.data_generator.hospital_db import build_hospital_db
from src.data_generator.pii_check import run_all
from src.data_generator.protocols_data import write_protocols

BASE = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera os dados sintéticos da Fase 3.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=None,
                        help="Limita o número de amostras (para testes rápidos).")
    args = parser.parse_args()

    data_dir = BASE / "data"
    protocols_dir = data_dir / "protocols"

    print("1/4 Gerando protocolos internos...")
    written = write_protocols(protocols_dir)
    print(f"   {len(written)} protocolos em {protocols_dir}")

    print("2/4 Construindo dataset instruction-style...")
    samples, stats = build_samples(seed=args.seed)
    if args.limit:
        samples = samples[: args.limit]
    for k, v in stats.items():
        print(f"   {k}: {v}")
    counts = write_splits(samples, data_dir / "fine_tune", seed=args.seed)
    print(f"   splits: {counts}")

    print("3/4 Construindo prontuários sintéticos (SQLite)...")
    db_counts = build_hospital_db(data_dir / "hospital.db", seed=args.seed)
    print(f"   hospital.db: {db_counts}")

    print("4/4 Verificando anonimização/PII...")
    ok = run_all(data_dir)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
