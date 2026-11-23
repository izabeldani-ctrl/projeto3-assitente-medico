"""Protocolos internos sintéticos do HospitalTech (dados 100% fictícios).

Cada protocolo é um documento Markdown versionado em ``data/protocols/``.
O conteúdo é usado como fonte de QA para o fine-tuning e como base de
conhecimento (RAG) do assistente.
"""

from __future__ import annotations

from pathlib import Path

DISCLAIMER = (
    "> Documento interno do HospitalTech — **dados 100% sintéticos** para fins "
    "educacionais. Não utilizar em atendimento real."
)

# --------------------------------------------------------------------------
# Protocolos
# --------------------------------------------------------------------------

PROTOCOLS: list[dict] = [
    {
        "code": "P001",
        "title": "Rastreamento mamográfico e classificação BI-RADS",
        "version": "2.1",
        "objective": (
            "Padronizar a interpretação dos exames de mamografia do HospitalTech e "
            "definir a conduta padronizada para cada categoria BI-RADS."
        ),
        "sections": [
            {
                "heading": "Indicações de rastreamento",
                "body": (
                    "Mulheres a partir de 40 anos devem realizar mamografia anual. "
                    "Pacientes com alto risco familiar (parente de primeiro grau com "
                    "câncer de mama antes dos 50 anos) iniciam o rastreamento aos "
                    "35 anos, com avaliação individual pelo mastologista."
                ),
            },
            {
                "heading": "Categorias BI-RADS e conduta",
                "body": (
                    "BI-RADS 0 (inconclusivo): solicitar ultrassonografia "
                    "complementar. BI-RADS 1 (negativa): manter rotina anual. "
                    "BI-RADS 2 (achado benigno): manter rotina anual. BI-RADS 3 "
                    "(provavelmente benigno): controle radiológico em 6 meses, "
                    "podendo ser antecipado a critério médico. BI-RADS 4 (suspeito, "
                    "subdividido em 4A/4B/4C): indicar biópsia percutânea. "
                    "BI-RADS 5 (altamente sugestivo de malignidade): biópsia imediata "
                    "e encaminhamento oncológico conforme o protocolo P002. BI-RADS 6 "
                    "(malignidade comprovada por biópsia): encaminhamento oncológico "
                    "imediato (P002)."
                ),
            },
            {
                "heading": "Prazo para emissão do laudo",
                "body": (
                    "O laudo deve ser emitido em até 5 dias úteis após a realização "
                    "do exame. Achados BI-RADS 4C ou 5 geram alerta automático para "
                    "a equipe médica responsável, conforme o protocolo P006."
                ),
            },
        ],
    },
    {
        "code": "P002",
        "title": "Fluxo de encaminhamento oncológico",
        "version": "1.4",
        "objective": (
            "Definir critérios e prazos para encaminhamento de pacientes ao "
            "serviço de oncologia do HospitalTech."
        ),
        "sections": [
            {
                "heading": "Critérios de encaminhamento",
                "body": (
                    "Encaminhar para oncologia pacientes com: BI-RADS 4C ou 5 em "
                    "mamografia ou ultrassonografia; BI-RADS 6; nódulo palpável "
                    "suspeito associado a alteração de imagem; resultado de biópsia "
                    "positivo para malignidade; ou crescimento documentado de lesão "
                    "previamente benigna."
                ),
            },
            {
                "heading": "Prazos de agendamento",
                "body": (
                    "Urgência: agendamento em até 7 dias corridos para BI-RADS 5 ou "
                    "biópsia positiva. Prioridade: até 14 dias para BI-RADS 4C. "
                    "Rotina: até 30 dias para os demais critérios. O descumprimento "
                    "de prazo gera alerta conforme o protocolo P006."
                ),
            },
            {
                "heading": "Documentação mínima",
                "body": (
                    "A solicitação de encaminhamento deve conter: laudo do exame de "
                    "imagem, resultado de biópsia (quando houver), histórico clínico "
                    "resumido e lista de exames pendentes conforme o protocolo P003."
                ),
            },
        ],
    },
    {
        "code": "P003",
        "title": "Exames mínimos pré-consulta oncológica",
        "version": "1.2",
        "objective": (
            "Garantir que todo paciente chegue à primeira consulta oncológica com "
            "os exames essenciais disponíveis, reduzindo retrabalho e atraso no "
            "diagnóstico."
        ),
        "sections": [
            {
                "heading": "Exames obrigatórios",
                "body": (
                    "Mamografia com laudo atualizado (menos de 90 dias); "
                    "ultrassonografia mamária quando indicada no laudo; laudo de "
                    "biópsia com estudo imuno-histoquímico (quando realizada); "
                    "hemograma completo, função renal e função hepática com até 30 "
                    "dias."
                ),
            },
            {
                "heading": "Regra de pendência",
                "body": (
                    "A consulta não deve ocorrer sem imagem atualizada. A equipe de "
                    "enfermagem revisa as pendências 48 horas antes da consulta e "
                    "solicita os exames faltantes. Exames atrasados há mais de 90 "
                    "dias geram alerta conforme o protocolo P006."
                ),
            },
            {
                "heading": "Validação humana",
                "body": (
                    "A lista de pendências gerada pelo sistema é sempre validada "
                    "pelo enfermeiro responsável antes de qualquer ação."
                ),
            },
        ],
    },
    {
        "code": "P004",
        "title": "Modelo de laudo de mamografia",
        "version": "1.3",
        "objective": (
            "Padronizar a estrutura dos laudos de mamografia emitidos pelo "
            "HospitalTech, garantindo completude e rastreabilidade."
        ),
        "sections": [
            {
                "heading": "Estrutura obrigatória do laudo",
                "body": (
                    "O laudo deve conter: (1) identificação do paciente e do "
                    "solicitante; (2) técnica do exame e incidências; (3) indicação "
                    "clínica; (4) descrição dos achados; (5) categoria BI-RADS "
                    "final; (6) conclusão diagnóstica; (7) recomendação de conduta "
                    "com base no protocolo P001; e (8) identificação e assinatura "
                    "do médico radiologista responsável."
                ),
            },
            {
                "heading": "Regras de redação",
                "body": (
                    "A conclusão deve sempre indicar a categoria BI-RADS e a "
                    "recomendação padronizada correspondente (P001). Termos "
                    "ambíguos são proibidos: usar a terminologia padronizada do "
                    "sistema de informação radiológica."
                ),
            },
        ],
    },
    {
        "code": "P005",
        "title": "Fluxo de dor torácica aguda",
        "version": "2.0",
        "objective": (
            "Definir o fluxo de avaliação de pacientes com dor torácica aguda na "
            "emergência do HospitalTech."
        ),
        "sections": [
            {
                "heading": "Avaliação inicial",
                "body": (
                    "Todo paciente com dor torácica aguda realiza eletrocardiograma "
                    "em até 10 minutos da admissão e coleta de troponina sérica. A "
                    "classificação de risco (alto, intermediário ou baixo) é "
                    "registrada pelo médico emergencista."
                ),
            },
            {
                "heading": "Fluxo por nível de risco",
                "body": (
                    "Alto risco (alteração isquêmica no ECG ou troponina elevada): "
                    "acionar imediatamente a equipe de cardiologia conforme o "
                    "protocolo P006 e manter monitorização contínua. Risco "
                    "intermediário: repetir troponina em 3 horas e manter em "
                    "observação. Baixo risco (ECG normal, troponina normal e dor "
                    "atípica): liberação após avaliação médica com orientação de "
                    "retorno."
                ),
            },
            {
                "heading": "Limites do assistente virtual",
                "body": (
                    "O assistente virtual não prescreve, não define alta e não "
                    "substitui a avaliação do médico emergencista em nenhuma etapa "
                    "deste fluxo (P007)."
                ),
            },
        ],
    },
    {
        "code": "P006",
        "title": "Critérios de alerta e acionamento da equipe médica",
        "version": "1.5",
        "objective": (
            "Definir níveis de alerta, canais de comunicação e responsáveis no "
            "acionamento da equipe médica."
        ),
        "sections": [
            {
                "heading": "Níveis de alerta",
                "body": (
                    "Informativo: exames pendentes ou próximos do vencimento; "
                    "enviado ao painel eletrônico do solicitante. Urgente: exame "
                    "crítico atrasado ou prazo de encaminhamento vencido (P002); "
                    "enviado ao solicitante e à coordenação. Crítico: dor torácica "
                    "de alto risco (P005), BI-RADS 5 sem agendamento em até 48 "
                    "horas ou resultado de biópsia positiva não visualizado; "
                    "acionamento imediato do plantão médico."
                ),
            },
            {
                "heading": "Conteúdo mínimo do alerta",
                "body": (
                    "Todo alerta deve conter: identificação do paciente, motivo, "
                    "protocolo de referência, prioridade, horário e responsável "
                    "pela triagem. Alertas críticos exigem confirmação de "
                    "recebimento pelo plantão."
                ),
            },
        ],
    },
    {
        "code": "P007",
        "title": "Protocolo de uso do Assistente Virtual",
        "version": "1.0",
        "objective": (
            "Definir os limites de atuação e as regras de segurança do assistente "
            "virtual médico do HospitalTech."
        ),
        "sections": [
            {
                "heading": "Limites de atuação",
                "body": (
                    "O assistente nunca prescreve medicamentos, nunca emite alta, "
                    "nunca firma diagnóstico definitivo e nunca substitui o "
                    "julgamento de um profissional de saúde. Toda sugestão de "
                    "conduta exige validação humana."
                ),
            },
            {
                "heading": "Explainability e auditoria",
                "body": (
                    "Toda resposta deve citar o protocolo interno utilizado (código "
                    "P00X) e, quando aplicável, os registros consultados. Todas as "
                    "interações são registradas em trilha de auditoria com "
                    "timestamp, usuário, pergunta e resposta."
                ),
            },
            {
                "heading": "Escopo",
                "body": (
                    "O assistente responde apenas sobre os protocolos internos do "
                    "HospitalTech. Perguntas fora do escopo recebem orientação para "
                    "buscar o canal adequado, sem tentativa de resposta clínica."
                ),
            },
        ],
    },
]


def protocol_markdown(proto: dict) -> str:
    lines = [
        f"# {proto['code']} — {proto['title']}",
        "",
        f"**Versão:** {proto['version']}",
        "",
        f"**Objetivo:** {proto['objective']}",
        "",
        DISCLAIMER,
        "",
    ]
    for section in proto["sections"]:
        lines += [f"## {section['heading']}", "", section["body"], ""]
    return "\n".join(lines)


def write_protocols(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for proto in PROTOCOLS:
        path = out_dir / f"{proto['code']}-{slug(proto['title'])}.md"
        path.write_text(protocol_markdown(proto), encoding="utf-8")
        written.append(path)
    return written


def slug(title: str) -> str:
    keep = "".join(
        c if c.isalnum() else "-" for c in title.lower()
    )
    return "-".join(part for part in keep.split("-") if part)
