"""Classe BaseConhecimento + função normalizar(): lê o JSON, lista categorias e busca com pontuação."""

import json
import os

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ü": "u", "ç": "c"}

SINAIS = "?!.,;:()-/\"'"
PALAVRAS_COMUNS = {"como", "para", "qual", "quais", "quando", "onde", "este",
                   "esta", "isso", "pode", "posso", "fazer", "sobre", "minha",
                   "meu", "tenho", "preciso", "quero", "voce", "sobre"}

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
MIN_LETRAS_TITULO = 4
LIMITE_ALTA = 6
LIMITE_MEDIA = 3

CAMPOS_OBRIGATORIOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
                       "documentos", "onde", "fonte", "verificado_em"]


def normalizar(texto):
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def nivel_confianca(pontos):
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return None


class BaseConhecimento:

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []
        self.erro = ""

    def carregar(self):
        self.orientacoes = []
        self.erro = ""
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.erro = f"Arquivo da base de conhecimento não encontrado: {self.caminho}"
            return False
        except json.JSONDecodeError:
            self.erro = f"O arquivo {self.caminho} está corrompido (JSON inválido)."
            return False
        except OSError as e:
            self.erro = f"Não foi possível abrir {self.caminho}: {e}"
            return False

        if not isinstance(dados, list):
            self.erro = "A base de conhecimento deve ser uma lista de orientações."
            return False

        ignorados = 0
        for item in dados:
            if isinstance(item, dict) and all(c in item for c in CAMPOS_OBRIGATORIOS):
                self.orientacoes.append(Orientacao.de_dicionario(item))
            else:
                ignorados += 1

        if ignorados:
            self.erro = f"{ignorados} registro(s) incompleto(s) foram ignorados."
        if not self.orientacoes:
            self.erro = self.erro or "A base de conhecimento está vazia."
            return False
        return True

    def categorias(self):
        lista = []
        for o in self.orientacoes:
            if o.categoria not in lista:
                lista.append(o.categoria)
        return lista

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        texto = normalizar(pergunta)
        pontos = 0

        for chave in orientacao.palavras_chave:
            if normalizar(chave) in texto:
                pontos += PONTOS_PALAVRA_CHAVE

        titulo = normalizar(orientacao.titulo)
        for palavra in set(texto.split()):
            if (len(palavra) >= MIN_LETRAS_TITULO
                    and palavra not in PALAVRAS_COMUNS
                    and f" {palavra} " in titulo):
                pontos += PONTOS_TITULO

        return pontos

    def buscar(self, pergunta):
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados
