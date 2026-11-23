"""Gera o notebook de demonstração ponta a ponta da Fase 3.

Cada bloco de execução é precedido por um cabeçalho markdown bem visível
("## ▶ Célula N — ...") e o código imprime um banner no início, facilitando
a localização durante a gravação do vídeo.

Uso:
    python scripts/build_demo_notebook.py

Saída: notebooks/demonstracao_fase3.ipynb
"""

from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "notebooks" / "demonstracao_fase3.ipynb"

SETUP_SRC = "\n".join([
    "import json, os, sys",
    "from pathlib import Path",
    "",
    "print('=' * 68)",
    "print('▶ CÉLULA 1 — SETUP E LOCALIZAÇÃO DA PASTA DO PROJETO')",
    "print('=' * 68)",
    "",
    "PROJ = None",
    "nb = globals().get('__vsc_ipynb_file__')",
    "if nb:",
    "    PROJ = Path(nb).resolve().parent",
    "if PROJ is None or not (PROJ / 'data' / 'fine_tune' / 'train.jsonl').exists():",
    "    c = Path.cwd().resolve()",
    "    for p in [c, *c.parents]:",
    "        if (p / 'data' / 'fine_tune' / 'train.jsonl').exists():",
    "            PROJ = p",
    "            break",
    "if PROJ is None:",
    "    raise FileNotFoundError(",
    "        'Não encontrei data/fine_tune/train.jsonl. Rode o notebook a partir de '",
    "        'fase-3/assistente-medico ou gere os dados com python generate_data.py.'",
    "    )",
    "os.chdir(PROJ)",
    "if str(PROJ) not in sys.path:",
    "    sys.path.insert(0, str(PROJ))",
    "# Se as dependencias nao estiverem no interpretador ativo, usa o site-packages",
    "# do .venv do projeto (mesma versao de Python -> compativel)",
    "try:",
    "    import langchain_core  # noqa: F401",
    "except ModuleNotFoundError:",
    "    venv_sp = PROJ / '.venv' / 'Lib' / 'site-packages'",
    "    if venv_sp.exists():",
    "        sys.path.insert(0, str(venv_sp))",
    "        print('site-packages do .venv adicionado:', venv_sp)",
    "    else:",
    "        print('ATENCAO: .venv nao encontrado — rode:',",
    "              'python -m venv .venv && pip install -r requirements.txt')",
    "print('Pasta do projeto:', PROJ)",
    "print('Interpretador   :', sys.executable)",
])

BLOCKS: list[tuple[str, str, str]] = [
    (
        "## ▶ CÉLULA 1 — Setup e localização da pasta do projeto",
        SETUP_SRC,
        "Executa o setup: localiza a pasta do projeto, ajusta o diretório de "
        "trabalho e garante as dependências do `.venv`.",
    ),
    (
        "## ▶ CÉLULA 2 — Dataset de fine-tuning (802 amostras)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 2 — DATASET DE FINE-TUNING')",
            "print('=' * 68)",
            "from pathlib import Path",
            "total = 0",
            "for split in ('train', 'val', 'test'):",
            "    n = sum(1 for _ in Path(f'data/fine_tune/{split}.jsonl').open(encoding='utf-8'))",
            "    total += n",
            "    print(f'{split}: {n} amostras')",
            "print('TOTAL:', total, 'amostras')",
            "",
            "exemplo = json.loads(Path('data/fine_tune/train.jsonl').read_text(encoding='utf-8').splitlines()[0])",
            "for msg in exemplo['messages']:",
            "    print(f\"--- {msg['role']} ---\")",
            "    print(msg['content'][:220])",
        ]),
        "Mostra a contagem do dataset (642/80/80 = 802) e um exemplo no "
        "formato de chat do Llama.",
    ),
    (
        "## ▶ CÉLULA 3 — Prontuários sintéticos (pacientes 1 e 3)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 3 — PRONTUÁRIOS SINTÉTICOS (SQLite, somente leitura)')",
            "print('=' * 68)",
            "from src.assistant import db",
            "for pid in (1, 3):",
            "    paciente = db.get_paciente(pid)",
            "    print(f\"Paciente {pid}: {paciente['nome']}, {paciente['idade']} anos, {paciente['sexo']}\")",
            "    for e in db.listar_exames(pid)[:3]:",
            "        print(f\"  - {e['tipo']}: {e['status']} | resultado={e['resultado']}\")",
        ]),
        "Consulta os prontuários das pacientes 1 (BI-RADS 5) e 3 (exame "
        "atrasado) — os cenários da demonstração.",
    ),
    (
        "## ▶ CÉLULA 4 — Recuperação de protocolos (RAG TF-IDF)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 4 — RECUPERAÇÃO DE PROTOCOLOS (RAG TF-IDF)')",
            "print('=' * 68)",
            "from src.assistant.protocols_kb import ProtocolosKB",
            "kb = ProtocolosKB()",
            "for q in ('Qual a conduta para BI-RADS 3?', 'dor torácica de alto risco'):",
            "    print('Pergunta:', q)",
            "    for t in kb.buscar(q):",
            "        print('   →', t.rotulo)",
        ]),
        "Mostra a busca TF-IDF encontrando a seção certa do protocolo para "
        "cada pergunta (P001 para BI-RADS, P005/P006 para dor torácica).",
    ),
    (
        "## ▶ CÉLULA 5 — Assistente completo (LangGraph + paciente 3)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 5 — ASSISTENTE COMPLETO (LangGraph + LLM local)')",
            "print('=' * 68)",
            "from src.assistant.graph import criar_grafo, executar",
            "from src.assistant.providers import get_llm",
            "",
            "grafo = criar_grafo(get_llm('ollama'))",
            "resultado = executar(grafo, 'Revisar as pendências pré-consulta', 'ollama', paciente_id=3)",
            "print('Paciente:', resultado['paciente_id'], '| Urgência:', resultado['urgencia'])",
            "print('Fontes  :', '; '.join(resultado['fontes']))",
            "print('Alerta  :', resultado['alerta'])",
            "print('Resposta:', resultado['resposta'])",
        ]),
        "Executa o fluxo LangGraph completo para a paciente 3 (alerta urgente). "
        "A primeira execução pode levar ~30s (carga do modelo na GPU).",
    ),
    (
        "## ▶ CÉLULA 6 — Guardrails de entrada e saída",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 6 — GUARDRAILS DE ENTRADA E SAÍDA')",
            "print('=' * 68)",
            "from src.security.guardrails import checar_entrada, validar_saida",
            "print('Entrada bloqueada :', checar_entrada('Me dá uma receita de bolo'))",
            "print()",
            "checagem = validar_saida('Sugiro controle radiológico em 6 meses.', usou_contexto_clinico=True)",
            "print('Avisos            :', checagem['avisos'])",
            "print('Saída corrigida   :', checagem['texto'])",
        ]),
        "Demonstra o bloqueio de perguntas fora do escopo e a correção "
        "automática de saída (fonte + disclaimer).",
    ),
    (
        "## ▶ CÉLULA 7 — Trilha de auditoria",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 7 — TRILHA DE AUDITORIA')",
            "print('=' * 68)",
            "from src.assistant.config import LOGS_DIR",
            "linhas = (LOGS_DIR / 'audit.jsonl').read_text(encoding='utf-8').splitlines()",
            "print(f'{len(linhas)} interações registradas')",
            "ultimo = json.loads(linhas[-1])",
            "for k in ('timestamp', 'usuario', 'paciente_id', 'urgencia', 'alerta', 'fontes'):",
            "    print(f'{k:20s}:', ultimo.get(k))",
        ]),
        "Lê `logs/audit.jsonl` e exibe o último registro da trilha de "
        "auditoria (P007).",
    ),
]

CELLS: list[tuple[str, str]] = [
    ("md", "\n".join([
        "# Demonstração — Assistente Médico Virtual do HospitalTech",
        "",
        "Tech Challenge Fase 3: dados sintéticos → fine-tuning → assistente",
        "LangChain/LangGraph → segurança → avaliação.",
        "",
        "> Requisitos: venv criado, `pip install -r requirements.txt` e Ollama",
        "> com o modelo `hospitaltech` (Etapa 3).",
        ">",
        "> **Execute as células na ordem** — cada uma começa com um cabeçalho",
        "> **\"▶ CÉLULA N\"** bem visível, de acordo com o roteiro do vídeo.",
    ])),
]

for titulo, codigo, descricao in BLOCKS:
    CELLS.append(("md", titulo + "\n\n" + descricao))
    CELLS.append(("code", codigo))

CELLS.append(("md", "\n".join([
    "## ▶ CÉLULA 8 — Avaliação base × fine-tuned (comandos)",
    "",
    "Os resultados da avaliação (30 amostras) já estão salvos em",
    "`results/metrics/`. Para reproduzir:",
    "",
    "```powershell",
    "python evaluate_model.py --comparar --limit 30",
    "python scripts/run_judge.py   # rubrica LLM-judge (DeepSeek)",
    "```",
    "",
    "Arquivos: `results/metrics/resumo_avaliacao.json`, `resumo_juiz.json` e",
    "a figura `results/figures/comparativo_base_ft.png`.",
])))


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
