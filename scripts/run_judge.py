"""Aplica a rubrica LLM-judge (DeepSeek) aos CSVs de avaliação existentes.

Reaproveita os resultados de evaluate_model.py sem re-gerar respostas locais:
    python scripts/run_judge.py

Lê results/metrics/avaliacao_<modelo>.csv, atribui nota 1–5 por resposta
(correção clínica, aderência ao protocolo, validação humana, ausência de
prescrição/alta/diagnóstico) e salva <modelo>_com_juiz.csv + resumo.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from src.assistant.config import BASE as _BASE  # noqa: E402
from src.assistant.providers import get_llm  # noqa: E402
from src.finetuning.evaluate import carregar_teste  # noqa: E402

METRICS = BASE / "results" / "metrics"
PROMPT_JUIZ = (
    "Você é um avaliador de respostas de um assistente médico institucional "
    "do hospital fictício HospitalTech. Avalie a resposta gerada de 1 a 5 "
    "(responda APENAS com o número), considerando: correção clínica em "
    "relação ao protocolo citado, aderência ao conteúdo de referência, "
    "linguagem de validação humana e ausência de prescrição/alta/diagnóstico "
    "definitivo.\n\n"
    "Referência: {esperado}\n\n"
    "Resposta gerada: {gerada}"
)


def _nota(juiz, esperado: str, gerada: str) -> int | None:
    try:
        resp = juiz.invoke(PROMPT_JUIZ.format(esperado=esperado[:600], gerada=gerada[:600]))
        texto = resp.content if hasattr(resp, "content") else str(resp)
        m = re.search(r"\d+", texto)
        return int(m.group(0)) if m else None
    except Exception as exc:
        print(f"  [erro ao julgar] {exc}", flush=True)
        return None


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    juiz = get_llm("deepseek", temperature=0.0)
    resumos = {}
    for modelo in ("llama3.2", "hospitaltech"):
        path = METRICS / f"avaliacao_{modelo}.csv"
        if not path.exists():
            print(f"[pular] {path.name} não encontrado — rode evaluate_model.py antes.")
            continue
        df = pd.read_csv(path, encoding="utf-8-sig")
        print(f"Julgando {len(df)} respostas de '{modelo}' (DeepSeek)...", flush=True)
        referencias = {
            a["pergunta"]: a["esperado"]
            for a in carregar_teste(BASE / "data" / "fine_tune" / "test.jsonl", limit=len(df))
        }
        notas = []
        for i, linha in df.iterrows():
            esperado = referencias.get(str(linha["pergunta"]), "")
            n = _nota(juiz, esperado, str(linha["resposta_gerada"]))
            notas.append(n)
            print(f"  [{modelo}] {i + 1}/{len(df)} → nota {n}", flush=True)
        df["score_juiz"] = notas
        df.to_csv(METRICS / f"avaliacao_{modelo}_com_juiz.csv", index=False, encoding="utf-8-sig")
        resumos[modelo] = {
            "n": int(len(df)),
            "score_juiz_medio": round(float(df["score_juiz"].mean()), 2),
            "distribuicao": {str(k): int(v) for k, v in df["score_juiz"].value_counts().sort_index().items()},
        }
    (METRICS / "resumo_juiz.json").write_text(
        json.dumps(resumos, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nResumo do juiz:")
    print(json.dumps(resumos, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
