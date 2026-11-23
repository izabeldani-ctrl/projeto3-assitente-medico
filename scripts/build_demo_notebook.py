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
        "## ▶ CÉLULA 2 — Geração dos dados sintéticos (generate_data.py)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 2 — GERAÇÃO DOS DADOS SINTÉTICOS (generate_data.py)')",
            "print('=' * 68)",
            "import sqlite3",
            "from pathlib import Path",
            "from src.data_generator.dataset_builder import build_samples, write_splits",
            "from src.data_generator.hospital_db import build_hospital_db",
            "from src.data_generator.pii_check import run_all",
            "from src.data_generator.protocols_data import write_protocols",
            "",
            "DATA_DIR = Path('data')",
            "print('1/4 Gerando protocolos internos...')",
            "escritos = write_protocols(DATA_DIR / 'protocols')",
            "print(f'   {len(escritos)} protocolos em data/protocols')",
            "print('2/4 Construindo dataset instruction-style...')",
            "amostras, stats = build_samples(seed=42)",
            "for k, v in stats.items():",
            "    print(f'   {k}: {v}')",
            "contagens = write_splits(amostras, DATA_DIR / 'fine_tune', seed=42)",
            "print(f'   splits: {contagens}')",
            "print('3/4 Construindo prontuários sintéticos (SQLite)...')",
            "try:",
            "    db_counts = build_hospital_db(DATA_DIR / 'hospital.db', seed=42)",
            "    print(f'   hospital.db: {db_counts}')",
            "except sqlite3.OperationalError as exc:",
            "    print('ATENÇÃO: hospital.db está bloqueado por outro processo.')",
            "    print('Reinicie o kernel: Kernel → Reiniciar e executar tudo.')",
            "    raise",
            "print('4/4 Verificando anonimização/PII...')",
            "ok = run_all(DATA_DIR)",
            "print('RESULTADO:', 'OK' if ok else 'PROBLEMAS ENCONTRADOS')",
        ]),
        "Executa exatamente o que o `python generate_data.py` faz: gera os 7 "
        "protocolos, o dataset de fine-tuning, o banco de prontuários e roda a "
        "verificação de PII (termina com RESULTADO: OK).",
    ),
    (
        "## ▶ CÉLULA 3 — Protocolos internos (P001–P007)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 3 — PROTOCOLOS INTERNOS (P001–P007)')",
            "print('=' * 68)",
            "from pathlib import Path",
            "for path in sorted(Path('data/protocols').glob('*.md')):",
            "    primeira = path.read_text(encoding='utf-8').splitlines()[0]",
            "    print(primeira)",
            "print()",
            "print('--- Trecho da P007 (limites do assistente) ---')",
            "p007 = next(p for p in Path('data/protocols').glob('P007*.md'))",
            "linhas = p007.read_text(encoding='utf-8').splitlines()",
            "inicio = next(i for i, l in enumerate(linhas) if 'Limites de atuação' in l)",
            "print('\\n'.join(linhas[inicio:inicio + 7]))",
        ]),
        "Lista os 7 protocolos e mostra o trecho de limites de atuação da "
        "P007 (nunca prescrever, nunca dar alta, nunca diagnosticar).",
    ),
    (
        "## ▶ CÉLULA 4 — Dataset de fine-tuning (802 amostras)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 4 — DATASET DE FINE-TUNING')",
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
        "## ▶ CÉLULA 5 — Prontuários sintéticos (pacientes 1 e 3)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 5 — PRONTUÁRIOS SINTÉTICOS (SQLite, somente leitura)')",
            "print('=' * 68)",
            "from src.assistant import db",
            "for pid in (1, 3):",
            "    paciente = db.get_paciente(pid)",
            "    print(f\"Paciente {pid}: {paciente['nome']}, {paciente['idade']} anos, {paciente['sexo']}\")",
            "    for e in db.listar_exames(pid)[:3]:",
            "        print(f\"  - {e['tipo']}: {e['status']} | resultado={e['resultado']}\")",
            "    print()",
        ]),
        "Consulta os prontuários das pacientes 1 (BI-RADS 5) e 3 (exame "
        "atrasado) — os cenários da demonstração.",
    ),
    (
        "## ▶ CÉLULA 6 — Modelo fine-tuned no Ollama (2 perguntas ao vivo)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 6 — MODELO FINE-TUNED NO OLLAMA')",
            "print('=' * 68)",
            "import json as _json",
            "import urllib.request",
            "from langchain_core.messages import HumanMessage, SystemMessage",
            "from langchain_ollama import ChatOllama",
            "from src.assistant.config import OLLAMA_BASE_URL, OLLAMA_MODEL, SYSTEM_PROMPT",
            "",
            "try:",
            "    with urllib.request.urlopen(OLLAMA_BASE_URL + '/api/tags', timeout=5) as r:",
            "        modelos = [m['name'] for m in _json.load(r)['models']]",
            "    print('Modelos no Ollama:', ', '.join(modelos))",
            "except Exception as exc:",
            "    print('ATENÇÃO: Ollama não está rodando (rode `ollama serve`).', exc)",
            "    raise SystemExit",
            "",
            "llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL,",
            "                temperature=0.2, num_ctx=2048, num_predict=256)",
            "perguntas = [",
            "    'Qual é a conduta para uma mamografia BI-RADS 3?',",
            "    'Prescreva um antibiótico para uma paciente com mastite.',",
            "]",
            "for q in perguntas:",
            "    print('-' * 68)",
            "    print('PERGUNTA:', q)",
            "    resp = llm.invoke([SystemMessage(SYSTEM_PROMPT), HumanMessage(q)])",
            "    print('RESPOSTA:', resp.content)",
            "print('-' * 68)",
        ]),
        "Lista os modelos do Ollama e faz as 2 perguntas da demo: conduta "
        "BI-RADS 3 (cita P001) e pedido de prescrição (recusado, P007). "
        "A primeira pergunta pode levar ~30s (carga do modelo).",
    ),
    (
        "## ▶ CÉLULA 7 — Recuperação de protocolos (RAG TF-IDF)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 7 — RECUPERAÇÃO DE PROTOCOLOS (RAG TF-IDF)')",
            "print('=' * 68)",
            "from src.assistant.protocols_kb import ProtocolosKB",
            "kb = ProtocolosKB()",
            "for q in ('Qual a conduta para BI-RADS 3?', 'dor torácica de alto risco'):",
            "    print('Pergunta:', q)",
            "    for t in kb.buscar(q):",
            "        print('   →', t.rotulo)",
            "    print()",
        ]),
        "Mostra a busca TF-IDF encontrando a seção certa do protocolo para "
        "cada pergunta (P001 para BI-RADS, P005/P006 para dor torácica).",
    ),
    (
        "## ▶ CÉLULA 8 — Assistente completo — paciente 3 (alerta urgente)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 8 — ASSISTENTE COMPLETO (LangGraph) — PACIENTE 3')",
            "print('=' * 68)",
            "from src.assistant.graph import criar_grafo, executar",
            "from src.assistant.providers import get_llm",
            "from run_assistant import _formatar",
            "",
            "grafo = criar_grafo(get_llm('ollama'))",
            "resultado = executar(grafo, 'Revisar as pendências pré-consulta', 'ollama', paciente_id=3)",
            "print(_formatar(resultado))",
        ]),
        "Executa o fluxo LangGraph completo para a paciente 3 (mamografia "
        "atrasada há mais de 90 dias → alerta urgente). ~30s na primeira vez.",
    ),
    (
        "## ▶ CÉLULA 9 — Assistente completo — paciente 1 (alerta crítico)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 9 — ASSISTENTE COMPLETO (LangGraph) — PACIENTE 1')",
            "print('=' * 68)",
            "resultado = executar(grafo, 'Revisar a conduta e as pendências da paciente 1', 'ollama', paciente_id=1)",
            "print(_formatar(resultado))",
        ]),
        "Cenário mais grave: paciente 1 com mamografia BI-RADS 5 → urgência "
        "crítica e alerta crítico (P006). Reaproveita o grafo da célula 8.",
    ),
    (
        "## ▶ CÉLULA 10 — Assistente em modo FAQ (sem paciente)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 10 — ASSISTENTE EM MODO FAQ (SEM PACIENTE)')",
            "print('=' * 68)",
            "resultado = executar(grafo, 'Qual é a conduta para uma mamografia BI-RADS 3?', 'ollama')",
            "print(_formatar(resultado))",
        ]),
        "Mesmo fluxo sem paciente: o assistente responde só com os protocolos "
        "internos (modo FAQ).",
    ),
    (
        "## ▶ CÉLULA 11 — Guardrails (entrada bloqueada + correção de saída)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 11 — GUARDRAILS DE ENTRADA E SAÍDA')",
            "print('=' * 68)",
            "from src.security.guardrails import checar_entrada, validar_saida",
            "print('--- Guardrail de ENTRADA (fora do escopo) ---')",
            "resultado = executar(grafo, 'Me dá uma receita de bolo', 'ollama')",
            "print('Bloqueada :', resultado['bloqueada'])",
            "print('Resposta  :', resultado['resposta'])",
            "print()",
            "print('--- Guardrail de SAÍDA (fonte + disclaimer) ---')",
            "checagem = validar_saida('Sugiro controle radiológico em 6 meses.', usou_contexto_clinico=True)",
            "print('Avisos          :', checagem['avisos'])",
            "print('Saída corrigida :', checagem['texto'])",
        ]),
        "Demonstra o bloqueio de perguntas fora do escopo (sem chamar a LLM) e "
        "a correção automática de saída (fonte + disclaimer).",
    ),
    (
        "## ▶ CÉLULA 12 — Trilha de auditoria",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 12 — TRILHA DE AUDITORIA')",
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
    (
        "## ▶ CÉLULA 13 — Segunda opinião com DeepSeek (modo híbrido)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 13 — SEGUNDA OPINIÃO COM DEEPSEEK (MODO HÍBRIDO)')",
            "print('=' * 68)",
            "try:",
            "    segunda = get_llm('deepseek')",
            "    resultado = executar(grafo, 'Revisar a conduta da paciente 1', 'ollama',",
            "                         paciente_id=1, segunda_opiniao_llm=segunda)",
            "    print(_formatar(resultado))",
            "except RuntimeError as exc:",
            "    print('Modo híbrido indisponível (sem DEEPSEEK_API_KEY no .env):', exc)",
        ]),
        "Mesma pergunta → resposta do modelo local fine-tuned + segunda opinião "
        "da API do DeepSeek (requer DEEPSEEK_API_KEY no .env).",
    ),
    (
        "## ▶ CÉLULA 14 — Testes automatizados (pytest)",
        "\n".join([
            "print('=' * 68)",
            "print('▶ CÉLULA 14 — TESTES AUTOMATIZADOS (pytest)')",
            "print('=' * 68)",
            "import subprocess",
            "py = str(PROJ / '.venv' / 'Scripts' / 'python.exe')",
            "res = subprocess.run([py, '-m', 'pytest', 'tests', '-q'],",
            "                    cwd=PROJ, capture_output=True, text=True, encoding='utf-8')",
            "print(res.stdout)",
            "if res.stderr:",
            "    print(res.stderr[-600:])",
            "print('exit code:', res.returncode)",
        ]),
        "Roda a suíte de testes com o Python do `.venv` — 20 testes passando.",
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
    "## ▶ CÉLULA 15 — Resultados da avaliação (resumo + figuras)",
    "",
    "Exibe o resumo da avaliação base × fine-tuned (ROUGE-L, fidelidade, juiz "
    "DeepSeek e prescrição) e mostra as duas figuras do projeto: o comparativo "
    "e a arquitetura do assistente.",
])))

CELLS.append(("code", "\n".join([
    "print('=' * 68)",
    "print('▶ CÉLULA 15 — RESULTADOS DA AVALIAÇÃO (RESUMO + FIGURAS)')",
    "print('=' * 68)",
    "import json",
    "from pathlib import Path",
    "",
    "resumo = json.loads(Path('results/metrics/resumo_avaliacao.json').read_text(encoding='utf-8'))",
    "juiz = json.loads(Path('results/metrics/resumo_juiz.json').read_text(encoding='utf-8'))",
    "",
    "print('--- ROUGE-L médio (30 amostras do holdout) ---')",
    "print('  Llama 3.2 (base)          :', resumo['llama3.2']['rougeL_medio'])",
    "print('  HospitalTech (fine-tuned) :', resumo['hospitaltech']['rougeL_medio'])",
    "print('--- Fidelidade de citação de protocolos ---')",
    "print('  base       :', round(resumo['llama3.2']['fidelidade_media'] * 100, 1), '%')",
    "print('  fine-tuned :', round(resumo['hospitaltech']['fidelidade_media'] * 100, 1), '%')",
    "print('--- Rubrica LLM-judge (DeepSeek, nota 1–5) ---')",
    "print('  base       :', juiz['llama3.2']['score_juiz_medio'])",
    "print('  fine-tuned :', juiz['hospitaltech']['score_juiz_medio'])",
    "print('--- Linguagem de prescrição detectada ---')",
    "print('  base:', resumo['llama3.2']['pct_prescricao'], '% | fine-tuned:',",
    "      resumo['hospitaltech']['pct_prescricao'], '%')",
    "",
    "import matplotlib.pyplot as plt",
    "import matplotlib.image as mpimg",
    "for nome, titulo in [",
    "    ('comparativo_base_ft.png', 'Comparativo base × fine-tuned (holdout, 30 amostras)'),",
    "    ('arquitetura_assistente.png', 'Arquitetura do assistente (LangGraph + LangChain)'),",
    "]:",
    "    img = mpimg.imread(Path('results/figures') / nome)",
    "    plt.figure(figsize=(12, 7))",
    "    plt.imshow(img)",
    "    plt.axis('off')",
    "    plt.title(titulo, fontsize=12)",
    "    plt.show()",
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
