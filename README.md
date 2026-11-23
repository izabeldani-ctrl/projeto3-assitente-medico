# Projeto 2 — Assistente Médico Virtual (Fase 3)

Assistente médico virtual do **HospitalTech** (cenário sintético): fine-tuning
de um LLM (Llama 3.2 3B) com protocolos internos + pipeline **LangChain** com
fluxos **LangGraph**, consultas a prontuários estruturados (SQLite), camada de
segurança (guardrails, auditoria e explainability) e modo híbrido com
**DeepSeek API**.

> 📋 Planejamento completo em [`../PLANO_EXECUCAO_FASE_3.md`](../PLANO_EXECUCAO_FASE_3.md)

## Status

- ⏳ Etapa 0 — Ambiente e acessos
- 🚧 Etapa 1 — Dados sintéticos (em andamento)
- ⏳ Etapas 2–3 — Fine-tuning (Colab + Unsloth) e integração Ollama
- ⏳ Etapas 4–6 — Assistente LangChain/LangGraph + segurança + DeepSeek
- ⏳ Etapas 7–10 — Avaliação, testes, documentação e vídeo

## Estrutura

```text
projeto2-assistente-medico/
├── generate_data.py         # gera protocolos, dataset e prontuários sintéticos
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
│   └── colab_finetuning_llama32_3b.ipynb
├── reports/
├── tests/
└── models/                  # Modelfile do Ollama (GGUF fica fora do git)
```

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

## Documentação

- Protocolos internos: `data/protocols/`
- Fine-tuning: `notebooks/colab_finetuning_llama32_3b.ipynb`
- Assistente: `src/assistant/` (em desenvolvimento)
- Relatório técnico: `reports/relatorio_fase3.md` (em desenvolvimento)
