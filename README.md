# Assistente Médico Virtual do HospitalTech — Tech Challenge Fase 3

Assistente médico virtual do **HospitalTech** (cenário sintético): fine-tuning
de um LLM (Llama 3.2 3B) com protocolos internos + pipeline **LangChain** com
fluxos **LangGraph**, consultas a prontuários estruturados (SQLite), camada de
segurança (guardrails, auditoria e explainability) e modo híbrido com
**DeepSeek API**.

> 📦 Repositório dedicado da Fase 3 · Modelo fine-tuned publicado no
> Hugging Face: [daniizabel/hospitaltech-llama3.2-3b-gguf](https://huggingface.co/daniizabel/hospitaltech-llama3.2-3b-gguf)

## Status

- ✅ Etapa 0 — Ambiente e acessos
- ✅ Etapa 1 — Dados sintéticos (protocolos P001–P007, dataset, prontuários)
- ✅ Etapas 2–3 — Fine-tuning (Colab + Unsloth, loss 0.31) e integração Ollama
- ✅ Etapas 4–6 — Assistente LangChain/LangGraph + segurança + DeepSeek híbrido
- ✅ Etapa 7 — Avaliação base × fine-tuned (ROUGE-L 0.119 → 0.533 · juiz 2.3 → 3.7)
- ✅ Etapa 8 — Testes automatizados (20 testes)
- ✅ Etapa 9 — Documentação (README, relatório, checklist)
- ⏳ Etapa 10 — Vídeo de demonstração (roteiro pronto em `reports/`)

## Estrutura

```text
.
├── generate_data.py         # gera protocolos, dataset e prontuários sintéticos
├── run_assistant.py         # CLI do assistente (LangGraph + guardrails)
├── evaluate_model.py        # avaliação base × fine-tuned (ROUGE-L, fidelidade)
├── data/
│   ├── protocols/           # protocolos internos P001–P007 (md)
│   ├── fine_tune/           # train/val/test.jsonl (chat template Llama 3.2)
│   └── hospital.db          # prontuários sintéticos (SQLite)
├── src/
│   ├── data_generator/      # geração dos dados + verificação de PII
│   ├── finetuning/          # utilidades de avaliação do fine-tuning
│   ├── assistant/           # LangChain + LangGraph
│   └── security/            # guardrails, logging, auditoria
├── notebooks/
│   ├── colab_finetuning_llama32_3b.ipynb  # fine-tuning (Unsloth/QLoRA)
│   └── demonstracao_fase3.ipynb           # demonstração ponta a ponta
├── scripts/
│   ├── build_colab_notebook.py  # regenera o notebook do Colab
│   ├── build_demo_notebook.py   # regenera o notebook de demonstração
│   ├── download_model.py        # baixa o GGUF do Hugging Face
│   ├── make_figures.py          # figuras do relatório
│   └── run_judge.py             # rubrica LLM-judge (DeepSeek)
├── tests/                   # 20 testes automatizados
├── results/
│   ├── metrics/             # CSVs de avaliação + resumos (auto + juiz)
│   └── figures/             # arquitetura + comparativo
└── models/                  # Modelfile do Ollama (GGUF fica fora do git)
```

> `reports/` (relatório técnico, guia do vídeo e checklist) fica fora do git,
> como nas fases anteriores.

## Como gerar os dados sintéticos

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python generate_data.py
```

## Como usar o assistente

```powershell
# Modo local (Ollama) — requer o modelo fine-tuned (Etapa 3):
#   huggingface-cli download SEU-USUARIO/hospitaltech-llama3.2-3b-gguf \
#       hospitaltech.Q4_K_M.gguf --local-dir models
#   ollama create hospitaltech -f models/Modelfile
python run_assistant.py "Qual a conduta para BI-RADS 3?"
python run_assistant.py "Revisar as pendências da paciente" --paciente 3

# Modo híbrido (DeepSeek): configure DEEPSEEK_API_KEY no .env
python run_assistant.py "Revisar a conduta da paciente 1" --provedor deepseek
python run_assistant.py "Revisar a conduta da paciente 1" --segunda-opiniao

# Testes
python -m pytest tests -q
```

## Segurança (Etapa 5)

- Guardrails de entrada (temas fora do escopo) e saída (prescrição/alta/
  diagnóstico, disclaimer, citação de fonte) em `src/security/guardrails.py`.
- Trilha de auditoria em `logs/audit.jsonl` (P007).
- Conexão ao prontuário **somente leitura** (`mode=ro`).

## Avaliação base × fine-tuned (Etapa 7)

```powershell
python evaluate_model.py --comparar --limit 30
python scripts/run_judge.py   # rubrica LLM-judge (DeepSeek) sobre os CSVs
```

Resultados no holdout (`data/fine_tune/test.jsonl`), 30 amostras por modelo:

| Modelo | ROUGE-L | Fidelidade de protocolos | Prescrição | Juiz (1–5) |
| --- | ---: | ---: | ---: | ---: |
| Llama 3.2 3B (base) | 0.119 | 0.18 | 0% | 2.3 |
| **HospitalTech (fine-tuned)** | **0.533** | **0.83** | **0%** | **3.7** |

Artefatos: `results/metrics/avaliacao_*.csv`, `avaliacao_*_com_juiz.csv`,
`resumo_avaliacao.json` e `resumo_juiz.json`.

## Documentação

- Protocolos internos: `data/protocols/`
- Fine-tuning: `notebooks/colab_finetuning_llama32_3b.ipynb`
- Assistente: `src/assistant/`
