"""Base de conhecimento dos protocolos internos (RAG leve com TF-IDF).

Carrega os arquivos Markdown de ``data/protocols/`` e recupera as seções
mais relevantes para uma pergunta — usadas para contextualizar a resposta
e para citar fontes (explainability, P007).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer

from .config import PROTOCOLS_DIR

RE_TITULO = re.compile(r"^#\s+(P\d{3})\s+[-–—]\s+(.+)$")
RE_SECAO = re.compile(r"^##\s+(.+)$")
RE_DISCLAIMER = re.compile(r"^>\s")
RE_METADADO = re.compile(r"^\*\*(Versão|Objetivo):\*\*")


@dataclass
class Trecho:
    codigo: str
    titulo: str
    secao: str
    texto: str

    @property
    def rotulo(self) -> str:
        return f"{self.codigo} — {self.titulo} (seção: {self.secao})"


class ProtocolosKB:
    def __init__(self, protocols_dir=PROTOCOLS_DIR):
        self.trechos = self._carregar(protocols_dir)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2), max_features=800, strip_accents="unicode"
        )
        self._matriz = self.vectorizer.fit_transform(
            [f"{t.codigo} {t.titulo} {t.secao} {t.texto}" for t in self.trechos]
        )

    @staticmethod
    def _carregar(protocols_dir) -> list[Trecho]:
        trechos: list[Trecho] = []
        for path in sorted(protocols_dir.glob("*.md")):
            texto = path.read_text(encoding="utf-8")
            titulo_atual = path.stem
            secao_atual = "Geral"
            corpo: list[str] = []
            primeira_linha = texto.splitlines()[0] if texto.strip() else ""
            match_titulo = RE_TITULO.search(primeira_linha)
            codigo = match_titulo.group(1) if match_titulo else path.stem.split("-")[0]
            if match_titulo:
                titulo_atual = match_titulo.group(2)

            for linha in texto.splitlines():
                linha = linha.strip()
                if (not linha or RE_TITULO.match(linha)
                        or RE_DISCLAIMER.match(linha) or RE_METADADO.match(linha)):
                    continue
                m = RE_SECAO.match(linha)
                if m:
                    if corpo:
                        trechos.append(Trecho(
                            codigo=codigo, titulo=titulo_atual,
                            secao=secao_atual, texto="\n".join(corpo).strip(),
                        ))
                    secao_atual = m.group(1)
                    corpo = []
                else:
                    corpo.append(linha)
            if corpo:
                trechos.append(Trecho(
                    codigo=codigo, titulo=titulo_atual,
                    secao=secao_atual, texto="\n".join(corpo).strip(),
                ))
        return trechos

    def buscar(self, pergunta: str, k: int = 3) -> list[Trecho]:
        if not self.trechos:
            return []
        scores = self._matriz @ self.vectorizer.transform([pergunta]).T
        indices = scores.toarray().ravel().argsort()[::-1][:k]
        return [self.trechos[i] for i in indices if scores.toarray().ravel()[i] > 0]
