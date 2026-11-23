"""Etapa 3 — Baixa o GGUF fine-tuned do Hugging Face e prepara o modelo local.

Uso:
    python scripts/download_model.py SEU-USUARIO/hospitaltech-llama3.2-3b-gguf

Depois de baixar, crie o modelo no Ollama:
    ollama create hospitaltech -f models/Modelfile
"""

from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DEST = BASE / "models" / "hospitaltech.Q4_K_M.gguf"


def main() -> int:
    parser = argparse.ArgumentParser(description="Baixa o GGUF fine-tuned do HF.")
    parser.add_argument("repo", help="ex.: seu-usuario/hospitaltech-llama3.2-3b-gguf")
    args = parser.parse_args()

    url = f"https://huggingface.co/{args.repo}/resolve/main/hospitaltech.Q4_K_M.gguf"
    DEST.parent.mkdir(parents=True, exist_ok=True)

    print(f"Baixando {url}")
    print(f"Destino: {DEST}")

    req = urllib.request.Request(url, headers={"User-Agent": "hospitaltech-download"})
    with urllib.request.urlopen(req) as resp, DEST.open("wb") as out:
        total = int(resp.headers.get("Content-Length", 0))
        baixado = 0
        while True:
            bloco = resp.read(1024 * 1024)
            if not bloco:
                break
            out.write(bloco)
            baixado += len(bloco)
            if total:
                pct = baixado * 100 // total
                print(f"\r{baixado / 1e6:6.1f} MB / {total / 1e6:.1f} MB ({pct}%)", end="")
    print("\nDownload concluído.")

    print("\nAgora crie o modelo no Ollama:")
    print(f"  ollama create hospitaltech -f {BASE / 'models' / 'Modelfile'}")
    print('  ollama run hospitaltech "Qual a conduta para BI-RADS 3?"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
