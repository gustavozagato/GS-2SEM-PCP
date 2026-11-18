"""Classe Assistente: conversa com o cidadão, guarda o histórico e calcula indicadores."""

import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import nivel_confianca

AVISO = "Aviso: este assistente NÃO é um canal oficial."
CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou", "ajudou",
              "tentativas", "tempo_segundos", "confianca", "pontos", "sessao",
              "nota_facilidade"]


def ler(texto):
    return input(texto).strip()


def tem_dado_pessoal(texto):
    digitos = sum(1 for c in texto if c.isdigit())
    return digitos >= 8 or "@" in texto


class Assistente:

    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.sessao = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.historico = self.carregar_historico()

    def carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return [d for d in dados if isinstance(d, dict)]
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, OSError):
            print("Aviso: o histórico estava corrompido. Um novo será criado.")
            try:
                os.replace(self.caminho_historico, self.caminho_historico + ".corrompido")
            except OSError:
                pass
        return []

    def salvar_historico(self):
        try:
            os.makedirs(os.path.dirname(self.caminho_historico) or ".", exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"Não foi possível salvar o histórico: {e}")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo, confianca=None, pontos=0):
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "confianca": confianca,
            "pontos": pontos,
            "sessao": self.sessao,
            "nota_facilidade": None,
        }
        self.historico.append(atendimento)
        self.salvar_historico()

    def perguntar_sim_nao(self, texto):
        while True:
            resposta = ler(texto).lower()
            if resposta in ("s", "n"):
                return resposta == "s"
            print("Resposta inválida. Digite apenas s (sim) ou n (não).")

    def escolher_numero(self, texto, maximo):
        while True:
            entrada = ler(texto)
            if entrada.isdigit() and 0 <= int(entrada) <= maximo:
                return int(entrada)
            print(f"Opção inválida. Digite um número de 0 a {maximo}.")

    def mostrar_resultado(self, resultados):
        pontos, melhor = resultados[0]
        print(f"\nConfiança da resposta: {nivel_confianca(pontos)} ({pontos} pontos)")
        melhor.exibir()

        alternativas = [(p, o) for p, o in resultados[1:3] if nivel_confianca(p)]
        if alternativas:
            print("\nVeja também:")
            for p, o in alternativas:
                print(f"  - {o.titulo} [{o.categoria}] ({p} pontos)")

    def sugerir(self):
        print("\nNão encontrei uma orientação segura para essa dúvida.")
        exemplos = [o.palavras_chave[0] for o in self.base.orientacoes[:8]]
        print("Tente outras palavras, por exemplo: " + ", ".join(exemplos) + ".")
        print("Ou use a navegação por categorias (opção 2 do menu): "
              + ", ".join(self.base.categorias()) + ".")
        print(AVISO)

    def perguntar(self):
        if not self.base.orientacoes:
            print("A base de conhecimento não está disponível.")
            return

        inicio = time.time()
        tentativas = 0
        encontrou = False
        ajudou = False
        ultima_pergunta = ""
        id_orientacao = None
        confianca = None
        pontos_finais = 0

        while True:
            texto = ler("\nDigite sua dúvida (0 para voltar): ")

            if texto == "0":
                break
            if not texto:
                print("Você não digitou nada. Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if tem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            ultima_pergunta = texto
            resultados = self.base.buscar(texto)

            if resultados and nivel_confianca(resultados[0][0]):
                pontos, melhor = resultados[0]
                encontrou = True
                id_orientacao = melhor.id
                confianca = nivel_confianca(pontos)
                pontos_finais = pontos
                self.mostrar_resultado(resultados)
                ajudou = self.perguntar_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
                if ajudou:
                    break
                print("Tudo bem. Tente reescrever com outras palavras ou veja as alternativas.")
            else:
                ajudou = False
                self.sugerir()

        if tentativas > 0:
            self.registrar("pergunta", ultima_pergunta, id_orientacao, encontrou,
                           ajudou, tentativas, round(time.time() - inicio, 1),
                           confianca, pontos_finais)

    def navegar(self):
        if not self.base.orientacoes:
            print("A base de conhecimento não está disponível.")
            return

        categorias = self.base.categorias()
        while True:
            print("\n=== Categorias ===")
            for i, categoria in enumerate(categorias, start=1):
                print(f"{i}. {categoria}")
            print("0. Voltar")
            escolha = self.escolher_numero("Escolha uma categoria: ", len(categorias))
            if escolha == 0:
                return
            self.navegar_categoria(categorias[escolha - 1])

    def navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            print(f"\n=== {categoria} ===")
            for i, o in enumerate(orientacoes, start=1):
                print(f"{i}. {o.titulo}")
            print("0. Voltar")
            escolha = self.escolher_numero("Escolha uma orientação: ", len(orientacoes))
            if escolha == 0:
                return

            inicio = time.time()
            orientacao = orientacoes[escolha - 1]
            orientacao.exibir()
            ajudou = self.perguntar_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            self.registrar("categoria", "", orientacao.id, True, ajudou, 1,
                           round(time.time() - inicio, 1))

    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            return {"total": 0}

        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudaram = [a for a in self.historico if a.get("ajudou")]
        tempos = [a.get("tempo_segundos", 0) for a in encontrados]
        tentativas = [a.get("tentativas", 1) for a in self.historico]

        notas = {}
        for a in self.historico:
            if a.get("nota_facilidade"):
                notas[a.get("sessao")] = a["nota_facilidade"]

        sem_solucao = []
        for a in self.historico:
            pergunta = a.get("pergunta", "")
            if pergunta and not (a.get("encontrou") and a.get("ajudou")) \
                    and pergunta not in sem_solucao:
                sem_solucao.append(pergunta)

        return {
            "total": total,
            "encontrada_pct": round(100 * len(encontrados) / total, 1),
            "acerto_pct": round(100 * len(ajudaram) / total, 1),
            "tempo_medio": round(sum(tempos) / len(tempos), 1) if tempos else 0.0,
            "tentativas_medias": round(sum(tentativas) / total, 1),
            "facilidade": round(sum(notas.values()) / len(notas), 1) if notas else None,
            "sem_solucao": sem_solucao,
        }

    def mostrar_indicadores(self):
        ind = self.indicadores()
        print("\n=== Indicadores ===")
        if ind["total"] == 0:
            print("Ainda não há atendimentos registrados.")
            return
        print(f"Atendimentos registrados:      {ind['total']}")
        print(f"Resposta encontrada (%):       {ind['encontrada_pct']}")
        print(f"Taxa de acerto: ajudou (%):    {ind['acerto_pct']}")
        print(f"Tempo médio para encontrar:    {ind['tempo_medio']} s")
        print(f"Tentativas por atendimento:    {ind['tentativas_medias']}")
        facilidade = ind["facilidade"] if ind["facilidade"] is not None else "sem notas ainda"
        print(f"Facilidade de uso (1 a 5):     {facilidade}")
        print("Dúvidas sem solução:")
        if ind["sem_solucao"]:
            for pergunta in ind["sem_solucao"]:
                print(f"  - {pergunta}")
        else:
            print("  (nenhuma)")

    def exportar_csv(self):
        try:
            os.makedirs(os.path.dirname(self.caminho_csv) or ".", exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
            print(f"CSV exportado em {self.caminho_csv} ({len(self.historico)} atendimentos).")
        except OSError as e:
            print(f"Não foi possível exportar o CSV: {e}")

    def pedir_nota(self):
        da_sessao = [a for a in self.historico if a.get("sessao") == self.sessao]
        if not da_sessao:
            return
        while True:
            entrada = ler("De 1 a 5, qual a facilidade de usar o assistente? ")
            if entrada.isdigit() and 1 <= int(entrada) <= 5:
                for atendimento in da_sessao:
                    atendimento["nota_facilidade"] = int(entrada)
                self.salvar_historico()
                return
            print("Nota inválida. Digite um número de 1 a 5.")

    def menu(self):
        print(f"\n===== {self.nome} =====")
        print("Orientações sobre leis de trânsito, com base em fontes oficiais.")
        print(AVISO)
        print("Não digite CPF, telefone ou e-mail.")
        while True:
            print("\n--- Menu ---")
            print("1. Fazer uma pergunta")
            print("2. Navegar por categorias")
            print("3. Ver indicadores")
            print("4. Exportar atendimentos (CSV)")
            print("0. Sair")
            opcao = self.escolher_numero("Escolha uma opção: ", 4)
            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.mostrar_indicadores()
            elif opcao == 4:
                self.exportar_csv()
            else:
                self.pedir_nota()
                self.exportar_csv()
                print("Obrigado por usar o Citizen Assist AI. Dirija com segurança!")
                return
