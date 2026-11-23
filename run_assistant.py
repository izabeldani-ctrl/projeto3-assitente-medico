"""CLI do Assistente Médico Virtual do HospitalTech.

Exemplos:
    python run_assistant.py "Qual a conduta para BI-RADS 3?"
    python run_assistant.py "Revisar pendências da paciente" --paciente 3
    python run_assistant.py "..." --provedor deepseek --segunda-opiniao
    python run_assistant.py "..." --verbose
"""

from __future__ import annotations

import argparse
import json

from src.assistant.config import LOGS_DIR
from src.assistant.graph import criar_grafo, executar
from src.assistant.providers import get_llm
from src.security.audit import AuditTrail
from src.security.logging_utils import get_logger


def _formatar(resultado: dict) -> str:
    linhas = ["=" * 72]
    linhas.append("ASSISTENTE MÉDICO VIRTUAL — HospitalTech (dados sintéticos)")
    linhas.append("=" * 72)
    linhas.append(f"Pergunta    : {resultado['pergunta']}")
    linhas.append(f"Provedor    : {resultado.get('provedor')}")
    linhas.append(f"Paciente    : {resultado.get('paciente_id') or '—'}")
    linhas.append(f"Urgência    : {resultado.get('urgencia', '—')}")
    linhas.append(f"Fontes      : {', '.join(resultado.get('fontes', [])) or '—'}")
    if resultado.get("alerta"):
        linhas.append(f"🚨 {resultado['alerta']}")
    if resultado.get("avisos"):
        linhas.append(f"Guardrails  : {'; '.join(resultado['avisos'])}")
    linhas.append("-" * 72)
    linhas.append(resultado["resposta"])
    if resultado.get("segunda_opiniao"):
        linhas.append("-" * 72)
        linhas.append(f"SEGUNDA OPINIÃO (DeepSeek):\n{resultado['segunda_opiniao']}")
    linhas.append("=" * 72)
    return "\n".join(linhas)


def main() -> int:
    parser = argparse.ArgumentParser(description="Assistente Médico Virtual do HospitalTech")
    parser.add_argument("pergunta", nargs="+", help="pergunta ou contexto do atendimento")
    parser.add_argument("--paciente", type=int, default=None,
                        help="id do paciente (dispensa a identificação pela LLM)")
    parser.add_argument("--provedor", choices=["ollama", "deepseek"], default="ollama")
    parser.add_argument("--segunda-opiniao", action="store_true",
                        help="gera uma segunda opinião com o DeepSeek")
    parser.add_argument("--verbose", action="store_true", help="imprime o estado completo")
    args = parser.parse_args()

    pergunta = " ".join(args.pergunta)
    logger = get_logger("hospitaltech.cli", log_file=LOGS_DIR / "assistant.log")

    llm = get_llm(args.provedor)
    segunda = get_llm("deepseek") if args.segunda_opiniao else None
    grafo = criar_grafo(llm)
    resultado = executar(grafo, pergunta, args.provedor,
                         paciente_id=args.paciente, segunda_opiniao_llm=segunda)

    AuditTrail(LOGS_DIR).registrar({
        "usuario": "medico-demo",
        "provedor": resultado.get("provedor"),
        "pergunta": resultado["pergunta"],
        "paciente_id": resultado.get("paciente_id"),
        "prontuario_consultado": bool((resultado.get("prontuario") or {}).get("exames")),
        "urgencia": resultado.get("urgencia"),
        "fontes": resultado.get("fontes", []),
        "alerta": resultado.get("alerta"),
        "avisos": resultado.get("avisos", []),
        "resposta": resultado["resposta"],
        "segunda_opiniao": resultado.get("segunda_opiniao"),
        "segunda_opiniao_provedor": resultado.get("segunda_opiniao_provedor"),
    })
    logger.info("interação registrada na trilha de auditoria")

    print(_formatar(resultado))
    if args.verbose:
        print("\n[ESTADO COMPLETO]\n" + json.dumps(
            {k: v for k, v in resultado.items()}, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
