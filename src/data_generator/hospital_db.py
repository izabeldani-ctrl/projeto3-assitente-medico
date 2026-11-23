"""Prontuários sintéticos do HospitalTech (SQLite) para o assistente.

Tabelas: pacientes, exames, alertas. Dados 100% fictícios com seed fixa.
Alguns casos são criados de forma determinística (BI-RADS 5, biópsia
positiva, exame atrasado, dor torácica de alto risco) para servirem de
cenários de demonstração dos fluxos LangGraph.
"""

from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from .names import FICTIONAL_FIRST_NAMES, FICTIONAL_LAST_NAMES

EXAM_TYPES = [
    "Mamografia",
    "Ultrassonografia mamária",
    "Biópsia percutânea",
    "Hemograma completo",
    "Função renal",
    "Função hepática",
    "Troponina sérica",
    "Eletrocardiograma (ECG)",
]

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    idade INTEGER NOT NULL,
    sexo TEXT NOT NULL,
    data_cadastro TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exames (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id),
    tipo TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pendente', 'realizado', 'atrasado')),
    data_solicitacao TEXT NOT NULL,
    data_realizacao TEXT,
    resultado TEXT
);

CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id),
    tipo TEXT NOT NULL,
    prioridade TEXT NOT NULL CHECK (prioridade IN ('informativo', 'urgente', 'critico')),
    mensagem TEXT NOT NULL,
    criado_em TEXT NOT NULL
);
"""


def build_hospital_db(path: Path, seed: int = 42) -> dict:
    rng = random.Random(seed)
    today = date(2026, 11, 22)

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    conn.executescript(CREATE_SQL)

    # ---- pacientes -------------------------------------------------------
    used = set()
    pacientes = []
    for i in range(30):
        while True:
            nome = f"{rng.choice(FICTIONAL_FIRST_NAMES)} {rng.choice(FICTIONAL_LAST_NAMES)}"
            if nome not in used:
                used.add(nome)
                break
        sexo = "feminino" if rng.random() < 0.7 else "masculino"
        idade = rng.randint(32, 78)
        cadastro = (today - timedelta(days=rng.randint(5, 540))).isoformat()
        pacientes.append((nome, idade, sexo, cadastro))
    conn.executemany(
        "INSERT INTO pacientes (nome, idade, sexo, data_cadastro) VALUES (?, ?, ?, ?)",
        pacientes,
    )

    # ---- exames ----------------------------------------------------------
    exames = []

    def add_exame(pac_id: int, tipo: str, status: str, dias_tras: int,
                  dias_ate_result: int | None = None, resultado: str | None = None):
        solicitacao = today - timedelta(days=dias_tras)
        realizacao = (
            (solicitacao + timedelta(days=dias_ate_result)).isoformat()
            if (status == "realizado" and dias_ate_result is not None)
            else None
        )
        exames.append((pac_id, tipo, status, solicitacao.isoformat(), realizacao, resultado))

    # Cenários determinísticos (demonstração dos fluxos):
    add_exame(1, "Mamografia", "realizado", 12, 7,
              "BI-RADS 5 — nódulo espiculado na mama direita")
    add_exame(2, "Biópsia percutânea", "realizado", 5, 3,
              "positivo para malignidade")
    add_exame(2, "Mamografia", "realizado", 40, 35, "BI-RADS 4C")
    add_exame(3, "Mamografia", "atrasado", 120, None, None)
    add_exame(4, "Eletrocardiograma (ECG)", "realizado", 1, 1,
              "supradesnivelamento de segmento ST")
    add_exame(4, "Troponina sérica", "realizado", 1, 1, "elevada")
    add_exame(5, "Ultrassonografia mamária", "pendente", 15, None, None)

    # Demais exames aleatórios:
    for pac_id in range(1, 31):
        n = rng.randint(2, 5)
        for _ in range(n):
            tipo = rng.choice(EXAM_TYPES)
            roll = rng.random()
            status = "realizado" if roll < 0.55 else ("pendente" if roll < 0.8 else "atrasado")
            dias_tras = rng.randint(1, 180)
            resultado = None
            dias_ate_result = None
            if status == "realizado":
                dias_ate_result = rng.randint(2, 10)
                if tipo == "Mamografia" or tipo == "Ultrassonografia mamária":
                    resultado = rng.choice(
                        ["BI-RADS 1", "BI-RADS 2", "BI-RADS 3", "BI-RADS 0"]
                    )
                elif tipo == "Biópsia percutânea":
                    resultado = "negativo para malignidade"
                elif tipo == "Troponina sérica":
                    resultado = "normal"
                elif tipo == "Eletrocardiograma (ECG)":
                    resultado = "sem alterações isquêmicas"
                else:
                    resultado = "sem alterações relevantes"
            add_exame(pac_id, tipo, status, dias_tras, dias_ate_result, resultado)

    conn.executemany(
        "INSERT INTO exames (paciente_id, tipo, status, data_solicitacao, data_realizacao, resultado) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        exames,
    )

    # ---- alertas ---------------------------------------------------------
    alertas = []

    def add_alerta(pac_id: int, tipo: str, prioridade: str, mensagem: str, dias_tras: int):
        alertas.append((pac_id, tipo, prioridade, mensagem,
                        (today - timedelta(days=dias_tras)).isoformat()))

    add_alerta(1, "achado de imagem", "critico",
               "Paciente com BI-RADS 5 sem agendamento oncológico em até 48 horas (P006).",
               1)
    add_alerta(2, "resultado de biópsia", "critico",
               "Resultado de biópsia positiva não visualizado pela equipe (P006).",
               0)
    add_alerta(3, "exame atrasado", "urgente",
               "Mamografia atrasada há mais de 90 dias — revisar pendências pré-consulta (P003, P006).",
               2)
    add_alerta(4, "dor torácica", "critico",
               "Dor torácica de alto risco: acionamento imediato da cardiologia (P005, P006).",
               0)
    add_alerta(5, "exame pendente", "informativo",
               "Ultrassonografia mamária pendente — painel do solicitante (P006).",
               1)

    conn.executemany(
        "INSERT INTO alertas (paciente_id, tipo, prioridade, mensagem, criado_em) VALUES (?, ?, ?, ?, ?)",
        alertas,
    )

    conn.commit()
    counts = {
        "pacientes": conn.execute("SELECT COUNT(*) FROM pacientes").fetchone()[0],
        "exames": conn.execute("SELECT COUNT(*) FROM exames").fetchone()[0],
        "alertas": conn.execute("SELECT COUNT(*) FROM alertas").fetchone()[0],
    }
    conn.close()
    return counts
