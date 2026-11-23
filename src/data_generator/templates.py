"""Templates de laudos, solicitações e fluxos (dados sintéticos).

Variantes de pergunta/contexto para data augmentation determinística.
"""

from __future__ import annotations

IDADES = ["38", "45", "52", "47", "61", "55", "68", "41"]

# --------------------------------------------------------------------------
# Laudos
# --------------------------------------------------------------------------

# (exame, [(achado, birads, recomendação)])
LAUDO_CASES: dict[str, list[tuple[str, str, str]]] = {
    "mamografia": [
        (
            "assimetria focal na mama direita, quadrante superior externo",
            "BI-RADS 4A",
            "biópsia percutânea conforme o protocolo P001",
        ),
        (
            "microcalcificações agrupadas de morfologia suspeita na mama esquerda",
            "BI-RADS 4B",
            "biópsia percutânea conforme o protocolo P001",
        ),
        (
            "nódulo espiculado de 1,8 cm no quadrante superior lateral da mama direita",
            "BI-RADS 5",
            "biópsia imediata e encaminhamento oncológico conforme os protocolos P001 e P002",
        ),
        (
            "ausência de achados suspeitos de malignidade",
            "BI-RADS 1",
            "manutenção da rotina anual de rastreamento conforme o protocolo P001",
        ),
        (
            "nódulo oval circunscrito de aspecto benigno na mama esquerda",
            "BI-RADS 2",
            "manutenção da rotina anual de rastreamento conforme o protocolo P001",
        ),
        (
            "assimetria focal de aspecto provavelmente benigno na mama direita",
            "BI-RADS 3",
            "controle radiológico em 6 meses conforme o protocolo P001",
        ),
        (
            "densidades assimétricas sem definição conclusiva em ambas as mamas",
            "BI-RADS 0",
            "ultrassonografia complementar conforme o protocolo P001",
        ),
    ],
    "ultrassonografia": [
        (
            "cisto simples anecoico de 1,2 cm na mama esquerda",
            "BI-RADS 2",
            "manutenção da rotina anual de rastreamento conforme o protocolo P001",
        ),
        (
            "nódulo hipoecoico irregular com sombra acústica posterior",
            "BI-RADS 4C",
            "biópsia percutânea e encaminhamento oncológico conforme os protocolos P001 e P002",
        ),
    ],
}

LAUDO_QUESTION_FORMS = [
    "Elabore o laudo de {exame} de uma paciente de {idade} anos com o seguinte achado: {achado}.",
    "Gere um modelo de laudo de {exame} preenchido para: paciente de {idade} anos, {achado}.",
    "Estruture o laudo de {exame} conforme o protocolo P004 para o achado: {achado}.",
]


def laudo_answer(exame: str, idade: str, achado: str, birads: str, rec: str) -> str:
    return (
        f"Segue o modelo de laudo de {exame} estruturado conforme o protocolo P004:\n\n"
        f"**Identificação:** paciente do sexo feminino, {idade} anos (dados sintéticos).\n"
        f"**Técnica:** {exame} digital em incidências padronizadas.\n"
        f"**Indicação clínica:** rastreamento / investigação de achado mamário.\n"
        f"**Achados:** {achado}.\n"
        f"**Categoria BI-RADS:** {birads}.\n"
        f"**Conclusão:** {birads} — {achado}.\n"
        f"**Recomendação:** {rec}.\n\n"
        "**Observação:** laudo elaborado em caráter de modelo — deve ser revisado e "
        "assinado pelo médico radiologista responsável (P004, P007)."
    )


# --------------------------------------------------------------------------
# Solicitações de procedimentos (sem prescrição)
# --------------------------------------------------------------------------

SOLICITACAO_TEMPLATES: list[dict] = [
    {
        "id": "solicitacao_exames_pre_consulta",
        "questions": [
            "Gere a solicitação de exames pré-consulta oncológica para uma paciente com BI-RADS 4C.",
            "Quais exames devo solicitar para a primeira consulta oncológica e como estruturar o pedido?",
            "Monte o pedido de exames conforme o protocolo P003.",
        ],
        "answers": [
            "Conforme o protocolo P003, a solicitação pré-consulta deve incluir: mamografia com laudo atualizado (<90 dias), ultrassonografia mamária quando indicada, biópsia com imuno-histoquímica (quando realizada) e laboratoriais (hemograma, função renal e hepática) com até 30 dias.\n\n**Estrutura do pedido:** identificação do paciente, justificativa clínica (BI-RADS 4C — P001), lista de exames da P003 e assinatura do médico solicitante.\n\n**Observação:** a lista de pendências gerada pelo sistema deve ser validada pelo enfermeiro responsável (P003, P007).",
            "Pela P003, monte o pedido com: mamografia atualizada, USG se indicada, biópsia com imuno-histoquímica se realizada e laboratoriais básicos. Campos obrigatórios: paciente, justificativa (P001), exames da P003 e assinatura do solicitante. Validação humana da lista de pendências é obrigatória (P007).",
        ],
    },
    {
        "id": "solicitacao_encaminhamento",
        "questions": [
            "Estruture o encaminhamento oncológico de uma paciente com biópsia positiva.",
            "Gere o formulário de encaminhamento oncológico conforme a P002.",
            "Como preencher o encaminhamento para oncologia?",
        ],
        "answers": [
            "Conforme o protocolo P002, o encaminhamento deve conter: laudo do exame de imagem, resultado de biópsia (positivo — critério de urgência), histórico clínico resumido e lista de exames pendentes (P003).\n\n**Prioridade:** urgência — agendamento em até 7 dias corridos (P002).\n\n**Observação:** o encaminhamento deve ser validado pelo médico assistente (P007).",
            "Pela P002: anexe laudo de imagem e biópsia, resuma o histórico clínico e liste as pendências da P003. Com biópsia positiva, classifique como urgência (≤7 dias). Validação do médico assistente é obrigatória (P007).",
        ],
    },
]

# --------------------------------------------------------------------------
# Fluxos (gatilhos do LangGraph / P006)
# --------------------------------------------------------------------------

FLUXO_TEMPLATES: list[dict] = [
    {
        "id": "fluxo_mamografia_atrasada",
        "questions": [
            "Paciente com mamografia solicitada há 120 dias ainda pendente: o que o sistema deve fazer?",
            "O exame de imagem está atrasado há 4 meses. Qual alerta é gerado?",
            "Como o sistema trata um exame crítico atrasado?",
        ],
        "answers": [
            "Conforme a P003 e a P006, exame atrasado há mais de 90 dias gera alerta urgente ao solicitante e à coordenação, com identificação do paciente, motivo, protocolo de referência e responsável pela triagem. A enfermagem revisa as pendências antes da consulta (P003).",
            "Pela P006, exame crítico com atraso superior a 90 dias dispara alerta urgente ao solicitante e à coordenação, registrado na trilha de auditoria.",
        ],
    },
    {
        "id": "fluxo_dor_toracica_alto_risco",
        "questions": [
            "Chegou na emergência uma paciente com dor torácica típica e supradesnivelamento de ST no ECG. Que fluxo o sistema dispara?",
            "ECG com supradesnivelamento de ST: qual o fluxo automatizado?",
            "Dor torácica de alto risco: o que o assistente deve acionar?",
        ],
        "answers": [
            "Pela P005, trata-se de alto risco: o sistema deve registrar a classificação, acionar imediatamente a equipe de cardiologia (alerta crítico — P006) e manter monitorização contínua. O alerta crítico exige confirmação de recebimento pelo plantão.",
            "Conforme a P005 e a P006, o fluxo dispara alerta crítico à cardiologia com confirmação obrigatória de recebimento e mantém a paciente em monitorização contínua.",
        ],
    },
    {
        "id": "fluxo_birads5_sem_agendamento",
        "questions": [
            "BI-RADS 5 sem agendamento oncológico em 48 horas: qual alerta o sistema emite?",
            "O prazo de urgência do encaminhamento venceu. O que acontece?",
            "Como o sistema trata BI-RADS 5 ainda sem consulta agendada?",
        ],
        "answers": [
            "Pela P006, BI-RADS 5 sem agendamento em até 48 horas configura alerta crítico: acionamento imediato do plantão médico, com confirmação de recebimento obrigatória. O prazo-alvo de agendamento é de até 7 dias corridos (P002).",
            "Conforme a P006, o sistema emite alerta crítico com acionamento imediato do plantão quando BI-RADS 5 permanece sem agendamento em 48 horas (prazo-alvo de 7 dias pela P002).",
        ],
    },
    {
        "id": "fluxo_biopsia_nao_visualizada",
        "questions": [
            "Biópsia com resultado positivo ainda não visualizada pela equipe: qual a ação do sistema?",
            "Resultado de biópsia positiva não lido: o que o fluxo dispara?",
            "Como o sistema garante que resultados críticos não fiquem sem leitura?",
        ],
        "answers": [
            "Pela P006, resultado de biópsia positiva não visualizado gera alerta crítico com acionamento imediato do plantão médico e confirmação de recebimento. Toda interação fica registrada na trilha de auditoria (P007).",
            "Conforme a P006, biópsia positiva sem leitura dispara alerta crítico ao plantão, com registro em auditoria (P007).",
        ],
    },
    {
        "id": "fluxo_exames_vencendo",
        "questions": [
            "Os exames laboratoriais de uma paciente vencem em 7 dias: há algum alerta?",
            "Exames próximos do vencimento: qual o tratamento do sistema?",
            "O sistema avisa quando exames estão perto de vencer?",
        ],
        "answers": [
            "Pela P006, exames pendentes ou próximos do vencimento geram alerta informativo ao painel eletrônico do solicitante, sem acionamento do plantão.",
            "Conforme a P006, o alerta é do nível informativo, enviado ao painel do solicitante — sem necessidade de acionamento do plantão.",
        ],
    },
    {
        "id": "fluxo_risco_intermediario",
        "questions": [
            "Dor torácica de risco intermediário: qual o fluxo na emergência?",
            "Troponina duvidosa em dor torácica: como conduzir?",
            "Qual a conduta para risco intermediário no fluxo de dor torácica?",
        ],
        "answers": [
            "Pela P005, no risco intermediário repete-se a troponina em 3 horas e a paciente permanece em observação até a decisão do médico emergencista.",
            "Conforme a P005, risco intermediário implica repetir troponina em 3 horas e manter a paciente em observação.",
        ],
    },
]

# --------------------------------------------------------------------------
# Paráfrases de contexto (prefixo opcional das perguntas)
# --------------------------------------------------------------------------

CONTEXT_PREFIXES = [
    "",
    "Caso clínico — paciente do sexo feminino, {idade} anos: ",
    "Pergunta da enfermagem — paciente de {idade} anos: ",
    "Dúvida rápida do plantão: ",
    "Contexto ambulatorial, paciente de {idade} anos: ",
    "Para registro no prontuário: ",
]
