"""Gera as figuras do relatório/vídeo da Fase 3.

Saídas (results/figures/):
- arquitetura_assistente.png    diagrama do fluxo LangGraph + recursos
- comparativo_base_ft.png       barras ROUGE-L e fidelidade (base × fine-tuned)

Uso: python scripts/make_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "results" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

AZUL = "#1F4E79"
AZUL_CLARO = "#DCE6F1"
VERDE_CLARO = "#E2EFDA"
LARANJA_CLARO = "#FBE5D6"
CINZA = "#BFBFBF"


def _box(ax, x, y, w, h, text, fc, bold=False):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.004",
        linewidth=1.0, edgecolor=AZUL, facecolor=fc, zorder=3,
    ))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=8.5, color=AZUL, fontweight="bold" if bold else "normal", zorder=4)


def _arrow(ax, x1, y1, x2, y2, dashed=False, color=AZUL):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11,
        linewidth=1.2, color=color, zorder=2,
        linestyle=(0, (4, 2)) if dashed else "solid",
    ))


def figura_arquitetura():
    fig, ax = plt.subplots(figsize=(10, 7.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    X, W = 0.04, 0.40
    passos = [
        ("1. Guardrail de entrada (P007)", LARANJA_CLARO, True),
        ("2. identificar_paciente (LLM)", AZUL_CLARO, False),
        ("3. verificar_exames (SQLite ro)", VERDE_CLARO, False),
        ("4. classificar_urgencia (P006)", VERDE_CLARO, False),
        ("5. recuperar_protocolos (TF-IDF)", VERDE_CLARO, False),
        ("6. responder (LLM + contexto)", AZUL_CLARO, False),
        ("7. emitir_alertas (P006)", LARANJA_CLARO, False),
        ("8. Guardrail de saída (fontes/disclaimer)", LARANJA_CLARO, True),
        ("Resposta final com fontes citadas", "#FFFFFF", True),
    ]
    H = 0.085
    GAP = 0.015
    Y_TOP = 0.90
    ys = [Y_TOP - i * (H + GAP) for i in range(len(passos))]
    for (texto, cor, bold), y in zip(passos, ys):
        _box(ax, X, y, W, H, texto, cor, bold=bold)
        if y != ys[0]:
            _arrow(ax, X + W / 2, y + H + GAP, X + W / 2, y + H)

    # Recursos laterais
    XR, WR = 0.62, 0.34
    recursos = [
        ("hospital.db (prontuários sintéticos)", 0.70, "3"),
        ("protocolos/ (P001–P007, md)", 0.50, "5"),
        ("Ollama — hospitaltech (fine-tuned)", 0.40, "6"),
        ("DeepSeek API (modo híbrido)", 0.30, "6"),
        ("logs/audit.jsonl (P007)", 0.10, "7"),
    ]
    for texto, y, alvo in recursos:
        _box(ax, XR, y, WR, 0.075, texto, "#F2F2F2")
        y_alvo = ys[int(alvo) - 1] + H / 2
        _arrow(ax, X + W, y_alvo, XR, y + 0.0375, dashed=True, color=CINZA)

    ax.set_title("Arquitetura do Assistente Médico Virtual (LangGraph + LangChain)",
                 fontsize=12, color=AZUL, fontweight="bold", pad=10)
    fig.tight_layout()
    fig.savefig(OUT / "arquitetura_assistente.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print("figura: arquitetura_assistente.png")


def figura_comparativo():
    metricas = ["ROUGE-L", "Fidelidade de\nprotocolos", "Juiz DeepSeek\n(1–5)"]
    base = [0.119, 0.18, 2.3]
    ft = [0.533, 0.83, 3.7]
    escalas = [1.0, 1.0, 5.0]

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    x = range(len(metricas))
    w = 0.32
    b1 = ax.bar([i - w / 2 for i in x], base, w, label="Llama 3.2 (base)",
                color=CINZA, edgecolor="#595959")
    b2 = ax.bar([i + w / 2 for i in x], ft, w, label="HospitalTech (fine-tuned)",
                color=AZUL, edgecolor="#16324f")
    for bars in (b1, b2):
        for r in bars:
            ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.035,
                    f"{r.get_height():.2f}", ha="center", fontsize=10,
                    color=AZUL, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(metricas, fontsize=10)
    ax.set_ylim(0, 5.2)
    ax.set_ylabel("Valor (R²-L e fidelidade: 0–1 · juiz: 1–5)", fontsize=9)
    ax.set_title("Comparativo base × fine-tuned (holdout, 30 amostras)",
                 fontsize=11.5, color=AZUL, fontweight="bold")
    ax.legend(fontsize=9, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "comparativo_base_ft.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print("figura: comparativo_base_ft.png")


if __name__ == "__main__":
    figura_arquitetura()
    figura_comparativo()
    print(f"Figuras salvas em {OUT}")
