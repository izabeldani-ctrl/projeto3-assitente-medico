"""FAQ de médicos do HospitalTech (dados sintéticos).

Entradas curadas de perguntas e respostas baseadas nos protocolos internos.
Cada entrada tem variantes de pergunta e de resposta para data augmentation
controlada (seed fixa).
"""

from __future__ import annotations

# Cada entrada: (id, protocolo, [variantes de pergunta], [variantes de resposta])
FAQ_ENTRIES: list[dict] = [
    {
        "id": "faq_rastreamento_idade",
        "protocol": "P001",
        "questions": [
            "A partir de qual idade o rastreamento mamográfico anual é indicado?",
            "Quando deve começar a mamografia anual de rastreamento?",
            "Qual é a indicação de rastreamento mamográfico conforme o protocolo?",
        ],
        "answers": [
            "Conforme o protocolo P001, mulheres a partir de 40 anos devem realizar mamografia anual. Pacientes com alto risco familiar (parente de primeiro grau com câncer de mama antes dos 50 anos) iniciam aos 35 anos, com avaliação individual pelo mastologista.",
            "O protocolo P001 indica mamografia anual a partir dos 40 anos. Em pacientes de alto risco familiar, o rastreamento começa aos 35 anos após avaliação do mastologista.",
        ],
    },
    {
        "id": "faq_birads0",
        "protocol": "P001",
        "questions": [
            "Qual a conduta para mamografia BI-RADS 0?",
            "O que fazer quando o laudo é classificado como BI-RADS 0?",
            "BI-RADS 0: como proceder segundo o protocolo?",
        ],
        "answers": [
            "Pela P001, a categoria BI-RADS 0 (inconclusivo) exige ultrassonografia complementar para conclusão diagnóstica.",
            "Segundo o protocolo P001, o achado BI-RADS 0 é inconclusivo e a conduta padronizada é solicitar ultrassonografia complementar.",
        ],
    },
    {
        "id": "faq_birads3",
        "protocol": "P001",
        "questions": [
            "Qual é a conduta indicada para BI-RADS 3?",
            "O que fazer com um achado provavelmente benigno (BI-RADS 3)?",
            "Mamografia BI-RADS 3: qual o seguimento recomendado?",
        ],
        "answers": [
            "De acordo com a P001, BI-RADS 3 (provavelmente benigno) tem conduta de controle radiológico em 6 meses, podendo ser antecipado a critério médico.",
            "O protocolo P001 recomenda controle radiológico em 6 meses para BI-RADS 3, com possibilidade de antecipação a critério do médico assistente.",
        ],
    },
    {
        "id": "faq_birads4",
        "protocol": "P001",
        "questions": [
            "Qual a conduta para um achado BI-RADS 4?",
            "BI-RADS 4: qual o próximo passo segundo o protocolo?",
            "O que indica o protocolo para lesões suspeitas BI-RADS 4?",
        ],
        "answers": [
            "Conforme a P001, achados BI-RADS 4 (suspeitos, subdivididos em 4A/4B/4C) têm indicação de biópsia percutânea para confirmação diagnóstica.",
            "Pelo protocolo P001, a categoria BI-RADS 4 indica biópsia percutânea da lesão suspeita.",
        ],
    },
    {
        "id": "faq_birads5",
        "protocol": "P001",
        "questions": [
            "Qual a conduta imediata para BI-RADS 5?",
            "O que fazer diante de mamografia altamente sugestiva de malignidade?",
            "BI-RADS 5: qual o fluxo definido no protocolo?",
        ],
        "answers": [
            "Segundo a P001, BI-RADS 5 (altamente sugestivo de malignidade) exige biópsia imediata e encaminhamento oncológico conforme a P002, com alerta para a equipe (P006).",
            "O protocolo P001 define que BI-RADS 5 requer biópsia imediata e encaminhamento oncológico pela P002; o prazo de agendamento é de até 7 dias corridos.",
        ],
    },
    {
        "id": "faq_birads_prazo_laudo",
        "protocol": "P001",
        "questions": [
            "Qual o prazo máximo para emissão do laudo de mamografia?",
            "Em quanto tempo o laudo da mamografia deve ser emitido?",
            "Existe prazo definido para liberar o laudo do exame de imagem?",
        ],
        "answers": [
            "A P001 estabelece que o laudo deve ser emitido em até 5 dias úteis após o exame; achados BI-RADS 4C ou 5 geram alerta automático à equipe médica (P006).",
            "Conforme o protocolo P001, o prazo máximo de emissão do laudo é de 5 dias úteis, com alerta automático para achados BI-RADS 4C ou 5.",
        ],
    },
    {
        "id": "faq_encaminhamento_criterios",
        "protocol": "P002",
        "questions": [
            "Quais são os critérios de encaminhamento oncológico?",
            "Quando devo encaminhar uma paciente para a oncologia?",
            "Que achados justificam encaminhamento ao serviço de oncologia?",
        ],
        "answers": [
            "Pela P002, encaminha-se à oncologia: BI-RADS 4C ou 5 em imagem, BI-RADS 6, nódulo palpável suspeito com alteração de imagem, biópsia positiva para malignidade ou crescimento documentado de lesão antes benigna.",
            "O protocolo P002 lista como critérios: BI-RADS 4C/5, BI-RADS 6, nódulo palpável suspeito com alteração de imagem, biópsia positiva e crescimento de lesão previamente benigna.",
        ],
    },
    {
        "id": "faq_encaminhamento_prazos",
        "protocol": "P002",
        "questions": [
            "Quais são os prazos de agendamento oncológico por prioridade?",
            "Em quantos dias a paciente com BI-RADS 5 deve ser atendida?",
            "Como funciona a priorização dos agendamentos de oncologia?",
        ],
        "answers": [
            "A P002 define: urgência em até 7 dias corridos para BI-RADS 5 ou biópsia positiva; prioridade em até 14 dias para BI-RADS 4C; e rotina em até 30 dias para os demais critérios.",
            "Conforme a P002, o agendamento é em até 7 dias para BI-RADS 5 ou biópsia positiva, 14 dias para BI-RADS 4C e 30 dias para os demais casos.",
        ],
    },
    {
        "id": "faq_encaminhamento_documentos",
        "protocol": "P002",
        "questions": [
            "Quais documentos são necessários no encaminhamento oncológico?",
            "O que não pode faltar na solicitação de encaminhamento?",
            "Qual a documentação mínima para encaminhar à oncologia?",
        ],
        "answers": [
            "Pela P002, a solicitação deve conter laudo do exame de imagem, resultado de biópsia (quando houver), histórico clínico resumido e a lista de exames pendentes conforme a P003.",
            "O protocolo P002 exige: laudo de imagem, biópsia quando disponível, histórico clínico resumido e lista de pendências da P003.",
        ],
    },
    {
        "id": "faq_exames_obrigatorios",
        "protocol": "P003",
        "questions": [
            "Quais exames são obrigatórios antes da primeira consulta oncológica?",
            "O que o paciente precisa trazer para a consulta inicial de oncologia?",
            "Qual a lista mínima de exames pré-consulta?",
        ],
        "answers": [
            "A P003 define como obrigatórios: mamografia com laudo de até 90 dias, ultrassonografia mamária quando indicada, laudo de biópsia com imuno-histoquímica (quando realizada) e laboratoriais (hemograma, função renal e hepática) com até 30 dias.",
            "Conforme a P003: mamografia atualizada (<90 dias), USG quando indicada, biópsia com imuno-histoquímica se realizada e exames laboratoriais básicos com até 30 dias.",
        ],
    },
    {
        "id": "faq_exames_pendencia",
        "protocol": "P003",
        "questions": [
            "Qual a regra quando há exames pendentes antes da consulta?",
            "A consulta pode ocorrer sem imagem atualizada?",
            "Como são tratadas as pendências pré-consulta?",
        ],
        "answers": [
            "Pela P003, a consulta não deve ocorrer sem imagem atualizada. A enfermagem revisa pendências 48 horas antes e solicita os faltantes; exames com mais de 90 dias de atraso geram alerta (P006).",
            "O protocolo P003 proíbe consulta sem imagem atualizada: a equipe de enfermagem revisa as pendências 48h antes e aciona os exames faltantes.",
        ],
    },
    {
        "id": "faq_laudo_estrutura",
        "protocol": "P004",
        "questions": [
            "O que não pode faltar em um laudo de mamografia?",
            "Qual a estrutura obrigatória do laudo de mamografia?",
            "Quais seções o laudo deve conter?",
        ],
        "answers": [
            "A P004 exige: identificação do paciente e solicitante, técnica e incidências, indicação clínica, achados, BI-RADS final, conclusão, recomendação de conduta (P001) e assinatura do radiologista.",
            "Conforme a P004, o laudo deve ter identificação, técnica, indicação clínica, achados, categoria BI-RADS, conclusão, recomendação padronizada pela P001 e assinatura do médico responsável.",
        ],
    },
    {
        "id": "faq_laudo_redacao",
        "protocol": "P004",
        "questions": [
            "Quais as regras de redação do laudo?",
            "Posso usar termos ambíguos no laudo de mamografia?",
            "Como deve ser redigida a conclusão do laudo?",
        ],
        "answers": [
            "Pela P004, a conclusão deve sempre indicar a categoria BI-RADS e a recomendação padronizada correspondente (P001); termos ambíguos são proibidos.",
            "O protocolo P004 proíbe termos ambíguos: a conclusão deve indicar a categoria BI-RADS e a recomendação padronizada conforme a P001.",
        ],
    },
    {
        "id": "faq_dor_avaliacao_inicial",
        "protocol": "P005",
        "questions": [
            "Qual a avaliação inicial da dor torácica aguda na emergência?",
            "O que deve ser feito nos primeiros minutos de uma dor torácica?",
            "Quais exames são feitos na admissão por dor torácica?",
        ],
        "answers": [
            "A P005 define que todo paciente com dor torácica aguda realiza ECG em até 10 minutos da admissão e coleta de troponina sérica, com classificação de risco registrada pelo médico emergencista.",
            "Conforme a P005: eletrocardiograma em até 10 minutos, troponina sérica e classificação de risco pelo médico emergencista.",
        ],
    },
    {
        "id": "faq_dor_alto_risco",
        "protocol": "P005",
        "questions": [
            "Como conduzir dor torácica de alto risco?",
            "ECG com alteração isquêmica: qual o fluxo?",
            "Quando acionar a cardiologia na dor torácica?",
        ],
        "answers": [
            "Pela P005, alto risco (alteração isquêmica no ECG ou troponina elevada) exige acionamento imediato da cardiologia conforme a P006 e monitorização contínua.",
            "O protocolo P005 indica acionamento imediato da equipe de cardiologia (P006) e monitorização contínua para dor torácica de alto risco.",
        ],
    },
    {
        "id": "faq_dor_baixo_risco",
        "protocol": "P005",
        "questions": [
            "Qual a conduta na dor torácica de baixo risco?",
            "ECG normal e troponina normal: o que fazer?",
            "Paciente com dor atípica e exames normais: conduta?",
        ],
        "answers": [
            "A P005 orienta que, em baixo risco (ECG normal, troponina normal e dor atípica), a liberação ocorre após avaliação médica com orientação de retorno.",
            "Conforme a P005, o paciente de baixo risco pode ser liberado após avaliação médica, com orientação de retorno.",
        ],
    },
    {
        "id": "faq_alerta_niveis",
        "protocol": "P006",
        "questions": [
            "Quais são os níveis de alerta da equipe médica?",
            "Como funciona a classificação de alertas no hospital?",
            "Que tipos de alerta o sistema pode emitir?",
        ],
        "answers": [
            "A P006 define três níveis: informativo (exames pendentes), urgente (exame crítico atrasado ou prazo vencido) e crítico (dor torácica de alto risco, BI-RADS 5 sem agendamento em 48h ou biópsia positiva não visualizada).",
            "Pela P006, os alertas são: informativo, urgente e crítico — o crítico exige acionamento imediato do plantão médico.",
        ],
    },
    {
        "id": "faq_alerta_conteudo",
        "protocol": "P006",
        "questions": [
            "O que um alerta deve conter?",
            "Qual o conteúdo mínimo de um alerta para a equipe?",
            "Como estruturar um alerta médico no sistema?",
        ],
        "answers": [
            "A P006 exige em todo alerta: identificação do paciente, motivo, protocolo de referência, prioridade, horário e responsável pela triagem; alertas críticos exigem confirmação de recebimento pelo plantão.",
            "Conforme a P006, o alerta deve conter paciente, motivo, protocolo de referência, prioridade, horário e responsável — com confirmação obrigatória nos críticos.",
        ],
    },
    {
        "id": "faq_assistente_prescricao",
        "protocol": "P007",
        "questions": [
            "O assistente virtual pode prescrever medicamentos?",
            "Posso pedir uma prescrição ao assistente?",
            "Quais os limites do assistente em relação a receitas?",
        ],
        "answers": [
            "Não. Pela P007, o assistente nunca prescreve medicamentos, nunca emite alta e nunca firma diagnóstico definitivo — toda conduta exige validação humana.",
            "O protocolo P007 proíbe prescrição, alta e diagnóstico definitivo pelo assistente; sugestões de conduta sempre exigem validação humana.",
        ],
    },
    {
        "id": "faq_assistente_explainability",
        "protocol": "P007",
        "questions": [
            "Como o assistente garante a rastreabilidade das respostas?",
            "De onde vêm as informações usadas nas respostas?",
            "O assistente cita fontes nas respostas?",
        ],
        "answers": [
            "Pela P007, toda resposta cita o protocolo interno utilizado (código P00X) e, quando aplicável, os registros consultados; todas as interações ficam em trilha de auditoria.",
            "O protocolo P007 exige citação do código do protocolo e dos registros consultados em cada resposta, além de auditoria completa das interações.",
        ],
    },
    {
        "id": "faq_assistente_escopo",
        "protocol": "P007",
        "questions": [
            "Sobre quais assuntos o assistente pode responder?",
            "O que acontece com perguntas fora do escopo?",
            "O assistente responde sobre qualquer tema médico?",
        ],
        "answers": [
            "Pela P007, o assistente responde apenas sobre os protocolos internos do HospitalTech; perguntas fora do escopo recebem orientação para buscar o canal adequado, sem resposta clínica.",
            "O protocolo P007 restringe o escopo aos protocolos internos; fora dele, o assistente orienta o canal adequado sem tentar responder clinicamente.",
        ],
    },
    {
        "id": "faq_alto_risco_familiar",
        "protocol": "P001",
        "questions": [
            "Como é definido o alto risco familiar para câncer de mama?",
            "Paciente com mãe com câncer de mama aos 45 anos: quando iniciar o rastreamento?",
            "O que muda no rastreamento para alto risco?",
        ],
        "answers": [
            "Pela P001, alto risco familiar é definido por parente de primeiro grau com câncer de mama antes dos 50 anos; o rastreamento inicia aos 35 anos com avaliação do mastologista.",
            "Conforme a P001, parente de primeiro grau com câncer de mama antes dos 50 anos define alto risco: rastreamento desde os 35 anos.",
        ],
    },
]

# Perguntas de recusa (reforço do P007 no fine-tuning)
REFUSAL_ENTRIES: list[dict] = [
    {
        "id": "recusa_antibiotico",
        "protocol": "P007",
        "questions": [
            "Prescreva um antibiótico para uma paciente com mastite.",
            "Quero uma receita de antibiótico, pode gerar?",
            "Gere uma prescrição de antibiótico oral.",
        ],
        "answers": [
            "Não posso prescrever medicamentos: esta atribuição é exclusiva do profissional habilitado (P007). Sugiro avaliação médica presencial para a paciente.",
            "Conforme a P007, o assistente não prescreve. Encaminhe o caso para avaliação do médico responsável.",
        ],
    },
    {
        "id": "recusa_alta",
        "protocol": "P007",
        "questions": [
            "Paciente com dor torácica melhorou: pode dar alta?",
            "Gere a alta hospitalar deste paciente.",
            "Autorize a alta do paciente da observação.",
        ],
        "answers": [
            "A emissão de alta é atribuição exclusiva do médico assistente (P007). O assistente pode apenas lembrar que o fluxo de baixo risco exige avaliação médica antes da liberação (P005).",
            "Não emito altas (P007). A liberação depende de avaliação médica, conforme o fluxo da P005.",
        ],
    },
    {
        "id": "recusa_diagnostico",
        "protocol": "P007",
        "questions": [
            "Este nódulo é câncer? Dê o diagnóstico definitivo.",
            "Feche o diagnóstico: a paciente tem câncer de mama?",
            "Qual o diagnóstico definitivo desta imagem?",
        ],
        "answers": [
            "Não firmo diagnóstico definitivo (P007). Posso indicar a conduta padronizada pela P001 para cada categoria BI-RADS, mas a conclusão diagnóstica cabe ao médico.",
            "Conforme a P007, o diagnóstico definitivo é atribuição médica. Posso auxiliar com a conduta padronizada (P001) para a categoria BI-RADS informada.",
        ],
    },
    {
        "id": "recusa_fora_escopo",
        "protocol": "P007",
        "questions": [
            "Qual a dose de insulina para diabéticos em geral?",
            "Como tratar hipertensão em gestantes?",
            "Me dê um resumo do tratamento de tuberculose.",
        ],
        "answers": [
            "Este tema está fora dos protocolos internos do HospitalTech. Conforme a P007, oriento buscar o canal clínico adequado; não posso responder clinicamente fora do escopo.",
            "Pergunta fora do escopo dos protocolos internos (P007). Recomendo consulta ao serviço clínico responsável.",
        ],
    },
]
