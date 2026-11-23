"""Testes do fluxo LangGraph com LLM fake (sem depender de Ollama/DeepSeek)."""

from __future__ import annotations

from types import SimpleNamespace

from src.assistant.graph import criar_grafo, executar


class FakeLLM:
    def __init__(self, respostas: list[str]):
        self.respostas = list(respostas)
        self.chamadas: list = []

    def invoke(self, messages, **kwargs):
        self.chamadas.append(messages)
        return SimpleNamespace(content=self.respostas.pop(0))


def _llm_fluxo() -> FakeLLM:
    return FakeLLM([
        '{"paciente_id": 1}',                                     # identificação
        "Conforme a P001, BI-RADS 5 exige biópsia e encaminhamento "
        "oncológico (P002). Validação humana obrigatória (P007).",  # resposta
    ])


def test_fluxo_completo_paciente_critico():
    llm = _llm_fluxo()
    grafo = criar_grafo(llm)
    resultado = executar(grafo, "Revisar a conduta da paciente 1", "ollama")
    assert resultado["paciente_id"] == 1
    assert resultado["urgencia"] == "critico"
    assert "ALERTA CRÍTICO" in resultado["alerta"]
    assert resultado["fontes"]
    assert "BI-RADS 5" in resultado["resposta"]
    assert len(llm.chamadas) == 2


def test_fluxo_sem_paciente_modo_faq():
    llm = FakeLLM([
        '{"paciente_id": null}',
        "Conforme a P001, o rastreamento inicia aos 40 anos. Validação humana (P007).",
    ])
    resultado = executar(criar_grafo(llm), "Quando começa o rastreamento?", "ollama")
    assert resultado["paciente_id"] is None
    assert resultado["urgencia"] == "sem alerta"
    assert resultado["alerta"] is None
    assert resultado["fontes"]  # recupera protocolos pela pergunta


def test_paciente_predefinido_pula_identificacao():
    llm = FakeLLM([
        "Conforme a P006, exame atrasado gera alerta urgente. Validação humana (P007).",
    ])
    resultado = executar(criar_grafo(llm), "Revisar pendências", "ollama", paciente_id=3)
    assert resultado["paciente_id"] == 3
    assert resultado["urgencia"] == "urgente"
    assert "URGENTE" in resultado["alerta"]
    assert len(llm.chamadas) == 1  # só a resposta


def test_guardrail_entrada_bloqueia_antes_da_llm():
    llm = FakeLLM([])
    resultado = executar(criar_grafo(llm), "Me dá uma receita de bolo", "ollama")
    assert resultado["bloqueada"]
    assert "P007" in resultado["resposta"]
    assert llm.chamadas == []


def test_segunda_opiniao_com_deepseek():
    llm = _llm_fluxo()
    segunda = FakeLLM([
        "Segunda opinião: manter encaminhamento conforme P002, validação humana (P007).",
    ])
    resultado = executar(criar_grafo(llm), "Revisar conduta da paciente 1", "ollama",
                         segunda_opiniao_llm=segunda)
    assert resultado["segunda_opiniao_provedor"] == "deepseek"
    assert "P002" in resultado["segunda_opiniao"]
    assert len(segunda.chamadas) == 1
