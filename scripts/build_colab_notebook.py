"""Gera o notebook de fine-tuning do Colab (Unsloth + Llama 3.2 3B).

Uso:
    python scripts/build_colab_notebook.py

Saída: notebooks/colab_finetuning_llama32_3b.ipynb
"""

from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "notebooks" / "colab_finetuning_llama32_3b.ipynb"

RAW_BASE = (
    "https://raw.githubusercontent.com/izabeldani-ctrl/projeto2/main/"
    "fase-3/projeto2-assistente-medico/data/fine_tune"
)

SYSTEM_PROMPT_CELL = (
    "SYSTEM = (\n"
    "    'Você é o Assistente Médico Virtual do HospitalTech, treinado com os '\n"
    "    'protocolos internos do hospital. Você responde dúvidas de médicos e da '\n"
    "    'enfermagem, estrutura laudos e fluxos conforme os protocolos internos e '\n"
    "    'sugere condutas padronizadas. Limites de atuação (P007): nunca prescreva '\n"
    "    'medicamentos, nunca emita alta, nunca firme diagnóstico definitivo e '\n"
    "    'sempre indique validação humana. Cite o código do protocolo utilizado '\n"
    "    '(ex.: P001). Responda em português do Brasil.'\n"
    ")\n"
)

CELLS: list[tuple[str, str]] = [
    # ---------------------------------------------------------------- markdown
    ("md", "\n".join([
        "# Fine-tuning do Assistente Médico do HospitalTech",
        "",
        "**Llama 3.2 3B Instruct + Unsloth (QLoRA)** — Tech Challenge Fase 3",
        "",
        "- Dataset: dados 100% sintéticos (protocolos P001–P007, FAQs, laudos, fluxos)",
        "  baixado do repositório `izabeldani-ctrl/projeto2`.",
        "- Tempo estimado na GPU T4 gratuita: **1–2 horas** (802 amostras, 3 epochs).",
        "- **Antes de executar:** crie um token de escrita no Hugging Face",
        "  (https://huggingface.co/settings/tokens) para publicar o GGUF no final.",
        "- Execução: menu **Ambiente de execução → Executar tudo**.",
    ])),
    # ---------------------------------------------------------------- code
    ("code", "\n".join([
        "#@title 1) Credenciais do Hugging Face",
        "import getpass",
        "",
        "HF_TOKEN = getpass.getpass('Token do Hugging Face (permissão de escrita): ')",
        "HF_USER = getpass.getpass('Usuário/org do Hugging Face (ex.: seu-usuario): ')",
        "OUT_MODEL = 'hospitaltech-llama3.2-3b'",
        "print('Configuração recebida.')",
    ])),
    ("code", "\n".join([
        "#@title 2) Instalar dependências (Unsloth)",
        "!pip install -q unsloth datasets huggingface_hub",
        "",
        "import torch",
        "print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NENHUMA — verifique Ambiente de execução > Alterar tipo de ambiente de execução > T4')",
    ])),
    ("code", "\n".join([
        "#@title 3) Baixar o dataset sintético do repositório",
        "import os, urllib.request",
        "",
        f"RAW_BASE = '{RAW_BASE}'",
        "os.makedirs('data', exist_ok=True)",
        "for split in ('train', 'val', 'test'):",
        "    url = f'{RAW_BASE}/{split}.jsonl'",
        "    urllib.request.urlretrieve(url, f'data/{split}.jsonl')",
        "    print(split, os.path.getsize(f'data/{split}.jsonl'), 'bytes')",
        "",
        "!head -c 400 data/train.jsonl",
    ])),
    ("code", "\n".join([
        "#@title 4) Carregar Llama 3.2 3B com QLoRA (4-bit)",
        "from unsloth import FastLanguageModel",
        "",
        "max_seq_length = 2048",
        "dtype = None",
        "load_in_4bit = True",
        "",
        "model, tokenizer = FastLanguageModel.from_pretrained(",
        "    model_name='unsloth/Llama-3.2-3B-Instruct-bnb-4bit',",
        "    max_seq_length=max_seq_length,",
        "    dtype=dtype,",
        "    load_in_4bit=load_in_4bit,",
        ")",
        "",
        "model = FastLanguageModel.get_peft_model(",
        "    model,",
        "    r=16,",
        "    target_modules=[",
        "        'q_proj', 'k_proj', 'v_proj', 'o_proj',",
        "        'gate_proj', 'up_proj', 'down_proj',",
        "    ],",
        "    lora_alpha=16,",
        "    lora_dropout=0,",
        "    bias='none',",
        "    use_gradient_checkpointing='unsloth',",
        "    random_state=42,",
        "    use_rslora=False,",
        "    loftq_config=None,",
        ")",
        "",
        "model.print_trainable_parameters()",
    ])),
    ("code", "\n".join([
        "#@title 5) Carregar e formatar o dataset (chat template)",
        "from datasets import load_dataset",
        "",
        "dataset = load_dataset(",
        "    'json',",
        "    data_files={'train': 'data/train.jsonl', 'val': 'data/val.jsonl', 'test': 'data/test.jsonl'},",
        ")",
        "",
        "def formatting_prompt(examples):",
        "    return {",
        "        'text': [",
        "            tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)",
        "            for msgs in examples['messages']",
        "        ]",
        "    }",
        "",
        "dataset = dataset.map(formatting_prompt, batched=True)",
        "print(dataset)",
        "print(dataset['train'][0]['text'][:400])",
    ])),
    ("code", "\n".join([
        "#@title 6) Treinar (SFT com LoRA) — ~1 a 2 horas na T4",
        "from trl import SFTTrainer",
        "from transformers import TrainingArguments",
        "",
        "trainer = SFTTrainer(",
        "    model=model,",
        "    tokenizer=tokenizer,",
        "    train_dataset=dataset['train'],",
        "    eval_dataset=dataset['val'],",
        "    dataset_text_field='text',",
        "    max_seq_length=max_seq_length,",
        "    dataset_num_proc=2,",
        "    packing=False,",
        "    args=TrainingArguments(",
        "        per_device_train_batch_size=2,",
        "        gradient_accumulation_steps=4,",
        "        warmup_steps=5,",
        "        num_train_epochs=3,",
        "        learning_rate=2e-4,",
        "        fp16=not torch.cuda.is_bf16_supported(),",
        "        bf16=torch.cuda.is_bf16_supported(),",
        "        logging_steps=10,",
        "        optim='adamw_8bit',",
        "        weight_decay=0.01,",
        "        lr_scheduler_type='linear',",
        "        seed=42,",
        "        output_dir='outputs',",
        "        report_to='none',",
        "        eval_strategy='steps',",
        "        eval_steps=50,",
        "        save_strategy='steps',",
        "        save_steps=50,",
        "    ),",
        ")",
        "",
        "trainer_stats = trainer.train()",
        "print(trainer_stats)",
    ])),
    # ---------------------------------------------------------------- markdown
    ("md", "\n".join([
        "## Teste rápido do modelo fine-tuned",
        "",
        "Duas perguntas de referência: uma de protocolo e uma de recusa (P007).",
    ])),
    ("code", "\n".join([
        "#@title 7) Geração de teste",
        "FastLanguageModel.for_inference(model)",
        "",
        SYSTEM_PROMPT_CELL,
        "def pergunta(q):",
        "    messages = [",
        "        {'role': 'system', 'content': SYSTEM},",
        "        {'role': 'user', 'content': q},",
        "    ]",
        "    inputs = tokenizer.apply_chat_template(",
        "        messages, tokenize=True, add_generation_prompt=True, return_tensors='pt'",
        "    ).to('cuda')",
        "    out = model.generate(input_ids=inputs, max_new_tokens=256, temperature=0.2, do_sample=True)",
        "    print('P:', q)",
        "    print('R:', tokenizer.decode(out[0][inputs.shape[1]:], skip_special_tokens=True))",
        "    print('-' * 70)",
        "",
        "pergunta('Qual é a conduta para uma mamografia BI-RADS 3?')",
        "pergunta('Prescreva um antibiótico para uma paciente com mastite.')",
    ])),
    ("code", "\n".join([
        "#@title 8) Salvar LoRA + modelo mesclado + exportar GGUF",
        "model.save_pretrained('hospitaltech_lora', tokenizer)",
        "model.save_pretrained_merged('hospitaltech_merged', tokenizer, save_method='merged_16bit')",
        "model.save_pretrained_gguf('hospitaltech_gguf', tokenizer, quantization_method='q4_k_m')",
        "",
        "import os",
        "print(os.listdir('hospitaltech_gguf'))",
    ])),
    ("code", "\n".join([
        "#@title 9) Publicar o GGUF no Hugging Face Hub",
        "from huggingface_hub import login, HfApi",
        "",
        "login(token=HF_TOKEN, add_to_git_credential=False)",
        "api = HfApi()",
        "repo_id = f'{HF_USER}/{OUT_MODEL}-gguf'",
        "api.create_repo(repo_id=repo_id, repo_type='model', exist_ok=True)",
        "api.upload_file(",
        "    path_or_fileobj='hospitaltech_gguf/unsloth.Q4_K_M.gguf',",
        "    path_in_repo='hospitaltech.Q4_K_M.gguf',",
        "    repo_id=repo_id,",
        "    repo_type='model',",
        ")",
        "print(f'Modelo publicado em https://huggingface.co/{repo_id}')",
    ])),
    # ---------------------------------------------------------------- markdown
    ("md", "\n".join([
        "## Próximos passos (máquina local)",
        "",
        "Baixe o GGUF publicado e crie o modelo no Ollama:",
        "",
        "```powershell",
        "huggingface-cli download SEU-USUARIO/hospitaltech-llama3.2-3b-gguf hospitaltech.Q4_K_M.gguf --local-dir models",
        "ollama create hospitaltech -f models/Modelfile",
        "ollama run hospitaltech \"Qual a conduta para BI-RADS 3?\"",
        "```",
        "",
        "O `Modelfile` do projeto aponta para `hospitaltech.Q4_K_M.gguf` e já está",
        "versionado no repositório (`fase-3/projeto2-assistente-medico/models/`).",
    ])),
]


def build() -> Path:
    cells = []
    for kind, source in CELLS:
        if kind == "md":
            cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [line + "\n" for line in source.splitlines()],
            })
        else:
            cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {"cellView": "form"},
                "outputs": [],
                "source": [line + "\n" for line in source.splitlines()],
            })

    notebook = {
        "cells": cells,
        "metadata": {
            "accelerator": "GPU",
            "colab": {"provenance": [], "gpuType": "T4"},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"Notebook gerado: {path} ({len(CELLS)} células)")
