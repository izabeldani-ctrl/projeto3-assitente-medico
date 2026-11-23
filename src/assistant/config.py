"""Configuração central do projeto (caminhos e variáveis de ambiente)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parents[2]
load_dotenv(BASE / ".env")

DATA_DIR = BASE / "data"
PROTOCOLS_DIR = DATA_DIR / "protocols"
DB_PATH = DATA_DIR / "hospital.db"
LOGS_DIR = BASE / "logs"
AUDIT_PATH = LOGS_DIR / "audit.jsonl"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "hospitaltech")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

SYSTEM_PROMPT = (
    "Você é o Assistente Médico Virtual do HospitalTech, treinado com os "
    "protocolos internos do hospital. Você responde dúvidas de médicos e da "
    "enfermagem, estrutura laudos e fluxos conforme os protocolos internos e "
    "sugere condutas padronizadas. Limites de atuação (P007): nunca prescreva "
    "medicamentos, nunca emita alta, nunca firme diagnóstico definitivo e "
    "sempre indique validação humana. Cite o código do protocolo utilizado "
    "(ex.: P001). Responda em português do Brasil."
)
