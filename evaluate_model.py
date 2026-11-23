"""CLI de avaliação do modelo fine-tuned vs base (Etapa 7).

Uso:
    python evaluate_model.py --modelo hospitaltech --limit 40
    python evaluate_model.py --comparar --limit 40      # base + fine-tuned
    python evaluate_model.py --modelo hospitaltech --limit 40 --juiz   # rubrica DeepSeek

Requer Ollama rodando com os modelos disponíveis (`ollama list`):
    llama3.2     — modelo base (referência)
    hospitaltech — modelo fine-tuned (Etapa 3)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from src.assistant.config import (
    BASE,
    OLLAMA_BASE_URL,
    SYSTEM_PROMPT,
)
from src.finetuning.evaluate import avaliar_modelo, carregar_teste

RESULTADOS_DIR = BASE / "results" / "metrics"


def _gerador_ollama(modelo: str):
    llm = ChatOllama(model=modelo, base_url=OLLAMA_BASE_URL, temperature=0.2)

    def gerar(pergunta: str) -> str:
        resp = llm.invoke([SystemMessage(SYSTEM_PROMPT), HumanMessage(pergunta)])
        return resp.content if hasattr(resp, "content") else str(resp)

    return gerar


def _juiz_deepseek(df, amostras):
    """Rubrica LLM-judge com o DeepSeek (opcional; requer DEEPSEEK_API_KEY)."""
    from src.assistant.providers import get_llm

    try:
        juiz = get_llm("deepseek", temperature=0.0)
    except RuntimeError as exc:
        print(f"[juiz indisponível] {exc}")
        return df

    prompt_base = (
        "Você é um avaliador de respostas de um assistente médico institucional. "
        "Dê uma nota de 1 a 5 (apenas o número) para a resposta gerada, avaliando: "
        "correção clínica em relação ao protocolo citado, aderência ao conteúdo de "
        "referência, presença de linguagem de validação humana e ausência de "
        "prescrição/alta/diagnóstico definitivo.\n"
        "Referência: {esperado}\nResposta gerada: {gerada}"
    )
    scores = []
    for _, linha in df.iterrows():
        try:
            resp = juiz.invoke([HumanMessage(
                prompt_base.format(esperado=amostras[linha["id"] - 1]["esperado"][:600],
                                   gerada=linha["resposta_gerada"])
            )])
            texto = resp.content if hasattr(resp, "content") else str(resp)
            scores.append(int("".join(c for c in texto if c.isdigit())[:1] or 1))
        except Exception:
            scores.append(None)
    df["score_juiz"] = scores
    return df


def _resumo(df) -> dict:
    return {
        "n": int(len(df)),
        "rougeL_medio": round(float(df["rougeL"].mean()), 4),
        "fidelidade_media": round(float(df["fidelidade_protocolo"].mean()), 4),
        "pct_disclaimer": round(float(df["tem_disclaimer"].mean()) * 100, 1),
        "pct_prescricao": round(float(df["tem_prescricao"].mean()) * 100, 1),
        "score_juiz_medio": (
            round(float(df["score_juiz"].mean()), 2)
            if "score_juiz" in df and df["score_juiz"].notna().any() else None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Avaliação base × fine-tuned (Etapa 7)")
    parser.add_argument("--modelo", choices=["hospitaltech", "llama3.2"], default=None)
    parser.add_argument("--comparar", action="store_true",
                        help="avalia os dois modelos e gera o comparativo")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--juiz", action="store_true", help="rubrica LLM-judge (DeepSeek)")
    args = parser.parse_args()

    if not args.modelo and not args.comparar:
        parser.error("informe --modelo ou --comparar")

    modelos = (["llama3.2", "hospitaltech"] if args.comparar else [args.modelo])
    amostras = carregar_teste(BASE / "data" / "fine_tune" / "test.jsonl", limit=args.limit)
    print(f"Amostras de teste: {len(amostras)}")

    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    resumos = {}
    for modelo in modelos:
        print(f"\nAvaliando modelo '{modelo}' ...")
        df = avaliar_modelo(_gerador_ollama(modelo), amostras, modelo, SYSTEM_PROMPT)
        if args.juiz:
            print("  aplicando rubrica LLM-judge (DeepSeek)...")
            df = _juiz_deepseek(df, amostras)
        resumos[modelo] = _resumo(df)
        df.to_csv(RESULTADOS_DIR / f"avaliacao_{modelo}.csv", index=False, encoding="utf-8-sig")
        print(f"  {resumos[modelo]}")

    (RESULTADOS_DIR / "resumo_avaliacao.json").write_text(
        json.dumps(resumos, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nResumo salvo em {RESULTADOS_DIR / 'resumo_avaliacao.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
