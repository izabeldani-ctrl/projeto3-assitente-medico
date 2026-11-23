"""Testes dos guardrails de entrada e saída (P007)."""

from __future__ import annotations

from src.security.guardrails import checar_entrada, validar_saida


def test_bloqueia_fora_de_escopo():
    assert checar_entrada("Me dá uma receita de bolo de chocolate") is not None
    assert checar_entrada("Quem ganhou o jogo de futebol ontem?") is not None
    assert "P007" in checar_entrada("Como faço um programa em Python?")


def test_libera_pergunta_clinica():
    assert checar_entrada("Qual a conduta para BI-RADS 3?") is None
    assert checar_entrada("Quais exames são obrigatórios pré-consulta?") is None


def test_saida_clinica_sem_fonte_recebe_fonte_e_disclaimer():
    resultado = validar_saida("Sugiro controle radiológico em 6 meses.",
                              usou_contexto_clinico=True)
    assert not resultado["ok"]
    assert "Fonte" in resultado["texto"]
    assert "validação humana" in resultado["texto"]


def test_saida_com_fonte_e_validacao_passa():
    texto = ("Conforme a P001, a conduta para BI-RADS 3 é controle em 6 meses. "
             "Validação humana é obrigatória (P007).")
    resultado = validar_saida(texto, usou_contexto_clinico=True)
    assert resultado["ok"]
    assert resultado["texto"] == texto


def test_detecta_linguagem_de_prescricao():
    resultado = validar_saida("Tome 500 mg por dia do medicamento.",
                              usou_contexto_clinico=False)
    assert any("proibida" in aviso for aviso in resultado["avisos"])
    assert "não prescreve" in resultado["texto"]


def test_saida_nao_clinica_nao_exige_fonte():
    resultado = validar_saida("Olá! Como posso ajudar?", usou_contexto_clinico=False)
    assert "Fonte" not in resultado["texto"]
    assert "validação humana" in resultado["texto"]  # disclaimer sempre presente
