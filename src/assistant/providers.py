"""Providers de LLM do assistente (configurável por ambiente).

- ``ollama``: modelo fine-tuned local (padrão) — OLLAMA_MODEL/URL no .env.
- ``deepseek``: API do DeepSeek via endpoint OpenAI-compatible (modo híbrido).
"""

from __future__ import annotations

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)


def get_llm(provedor: str = "ollama", temperature: float = 0.2):
    provedor = (provedor or "ollama").lower()
    if provedor == "ollama":
        return ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=temperature,
        )
    if provedor == "deepseek":
        if not DEEPSEEK_API_KEY:
            raise RuntimeError(
                "DEEPSEEK_API_KEY não configurada. Copie .env.example para .env "
                "e preencha a chave (ou use --provedor ollama)."
            )
        return ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            temperature=temperature,
        )
    raise ValueError(f"provedor desconhecido: {provedor!r} (use 'ollama' ou 'deepseek')")
