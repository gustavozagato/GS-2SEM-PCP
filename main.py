"""Citizen Assist AI - assistente de orientação sobre leis de trânsito (terminal)."""

import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(PASTA, "data")


def main():
    base = BaseConhecimento(os.path.join(DATA, "base_conhecimento.json"))
    carregou = base.carregar()
    if base.erro:
        print(f"Aviso: {base.erro}")
    if not carregou:
        print("O assistente vai abrir, mas sem orientações até a base ser corrigida.")

    assistente = Assistente("Citizen Assist AI", base,
                            os.path.join(DATA, "historico.json"),
                            os.path.join(DATA, "atendimentos.csv"))
    try:
        assistente.menu()
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado pelo usuário. Até logo!")


if __name__ == "__main__":
    main()
