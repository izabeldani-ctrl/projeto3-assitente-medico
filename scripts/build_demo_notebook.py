"""Gera o notebook de demonstração ponta a ponta da Fase 3.

Uso:
    python scripts/build_demo_notebook.py

Saída: notebooks/demonstracao_fase3.ipynb
"""

from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "notebooks" / "demonstracao_fase3.ipynb"

CELLS: list[tuple[str, str]] = [
    ("md", "\n".join([
        "# Demonstração — Assistente Médico Virtual do HospitalTech",
        "",
        "Tech Challenge Fase 3: dados sintéticos → fine-tuning → assistente",
        "LangChain/LangGraph → segurança → avaliação.",
        "",
        "> Requisitos: venv criado, `pip install -r requirements.txt` e Ollama",
        "> com o modelo `hospitaltech` (Etapa 3).",
    ])),
    ("code", "\n".join([
        "import json, sys",
        "from pathlib import Path",
        "sys.path.insert(0, str(Path.cwd()))",
        "",
        "print('Demonstração da Fase 3 — Assistente Médico Virtual (dados sintéticos)')",
    ])),
    ("code", "\n".join([
        "# 1) Dataset de fine-tuning",
        "from pathlib import Path",
        "for split in ('train', 'val', 'test'):",
        "    n = sum(1 for _ in Path(f'data/fine_tune/{split}.jsonl').open(encoding='utf-8'))",
        "    print(f'{split}: {n} amostras')",
        "",
        "exemplo = json.loads(Path('data/fine_tune/train.jsonl').read_text(encoding='utf-8').splitlines()[0])",
        "for msg in exemplo['messages']:",
        "    print(f\"--- {msg['role']} ---\")",
        "    print(msg['content'][:220])",
    ])),
    ("code", "\n".join([
        "# 2) Prontuários sintéticos (SQLite, somente leitura)",
        "from src.assistant import db",
        "for pid in (1, 3):",
        "    paciente = db.get_paciente(pid)",
        "    print(f\"Paciente {pid}: {paciente['nome']}, {paciente['idade']} anos, {paciente['sexo']}\")",
        "    for e in db.listar_exames(pid)[:3]:",
        "        print(f\"  - {e['tipo']}: {e['status']} | resultado={e['resultado']}\")",
    ])),
    ("code", "\n".join([
        "# 3) Recuperação de protocolos (RAG TF-IDF)",
        "from src.assistant.protocols_kb import ProtocolosKB",
        "kb = ProtocolosKB()",
        "for q in ('Qual a conduta para BI-RADS 3?', 'dor torácica de alto risco'):",
        "    print('Pergunta:', q)",
        "    for t in kb.buscar(q):",
        "        print('   →', t.rotulo)",
    ])),
    ("code", "\n".join([
        "# 4) Assistente completo (LangGraph + LLM fine-tuned local)",
        "from src.assistant.graph import criar_grafo, executar",
        "from src.assistant.providers import get_llm",
        "",
        "grafo = criar_grafo(get_llm('ollama'))",
        "resultado = executar(grafo, 'Revisar as pendências pré-consulta', 'ollama', paciente_id=3)",
        "print('Paciente:', resultado['paciente_id'], '| Urgência:', resultado['urgencia'])",
        "print('Fontes  :', '; '.join(resultado['fontes']))",
        "print('Alerta  :', resultado['alerta'])",
        "print('Resposta:', resultado['resposta'])",
    ])),
    ("code", "\n".join([
        "# 5) Guardrails (entrada e saída)",
        "from src.security.guardrails import checar_entrada, validar_saida",
        "print('Entrada bloqueada :', checar_entrada('Me dá uma receita de bolo'))",
        "print()",
        "checagem = validar_saida('Sugiro controle radiológico em 6 meses.', usou_contexto_clinico=True)",
        "print('Avisos            :', checagem['avisos'])",
        "print('Saída corrigida   :', checagem['texto'])",
    ])),
    ("code", "\n".join([
        "# 6) Trilha de auditoria",
        "from src.assistant.config import LOGS_DIR",
        "linhas = (LOGS_DIR / 'audit.jsonl').read_text(encoding='utf-8').splitlines()",
        "print(f'{len(linhas)} interações registradas')",
        "ultimo = json.loads(linhas[-1])",
        "print({k: ultimo[k] for k in ('timestamp', 'usuario', 'paciente_id', 'urgencia', 'alerta')})",
    ])),
    ("md", "\n".join([
        "## Avaliação (Etapa 7)",
        "",
        "```powershell",
        "python evaluate_model.py --comparar --limit 20",
        "```",
        "",
        "Resultados em `results/metrics/avaliacao_*.csv` e `resumo_avaliacao.json`.",
    ])),
]


def build() -> Path:
    cells = []
    for kind, source in CELLS:
        if kind == "md":
            cells.append({"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)})
        else:
            cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": source.splitlines(True),
            })
    notebook = {
        "cells": cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python3"},
                     "language_info": {"name": "python"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    return OUT


if __name__ == "__main__":
    print(f"Notebook gerado: {build()} ({len(CELLS)} células)")
