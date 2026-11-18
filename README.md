# Citizen Assist AI — Orientação sobre Leis de Trânsito

Assistente de terminal em Python que responde dúvidas sobre **leis de trânsito** usando apenas uma base de conhecimento verificada (JSON), mostrando sempre a **fonte**, a **data de verificação** e o aviso de que **não é um canal oficial**. Não coleta dados pessoais.

> Global Solution 2026.2 — Pensamento Computacional e Automação com Python (FIAP) — desafio **CitizenTech**

## Integrantes

| Nome | RM |
|------|----|
Gustavo Zagato Bottechia | 569420
Davi Q. Zuolo | 571669
Daniel Vilela Mana | 571632

## Público e problema escolhidos

**Público:** condutores e futuros condutores, principalmente jovens que estão tirando ou acabaram de tirar a CNH.

**Problema:** as regras de trânsito (valores de multa, pontos, recursos, Lei Seca, cadeirinha) estão espalhadas, em linguagem técnica e misturadas com sites de despachantes e blogs que parecem oficiais. O assistente reúne respostas curtas, em linguagem simples, sempre com a fonte e a data em que a equipe conferiu a informação.

## ODS relacionados

- **ODS 3 – Saúde e Bem-Estar** (meta 3.6: reduzir mortes e lesões no trânsito)
- **ODS 11 – Cidades e Comunidades Sustentáveis** (meta 11.2: sistemas de transporte seguros)
- **ODS 16 – Paz, Justiça e Instituições Eficazes** (meta 16.10: acesso público à informação)

## Como executar

Requisitos: Python 3.8 ou mais novo. **Não usa bibliotecas externas.**

```bash
git clone https://github.com/gustavozagato/GS-2SEM-PCP.git
cd citizen-assist-ai
python main.py
```

Menu principal:

1. Fazer uma pergunta (texto livre, busca com pontuação)
2. Navegar por categorias (0 para voltar em todas as telas)
3. Ver indicadores
4. Exportar atendimentos para CSV
0. Sair (pede nota de facilidade de 1 a 5 e exporta o CSV)

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py                  # ponto de entrada
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # classe BaseConhecimento + normalizar()
├── assistente.py            # classe Assistente
└── data/
    ├── base_conhecimento.json   # 14 orientações, 5 categorias
    ├── historico.json           # gerado a cada atendimento
    └── atendimentos.csv         # exportado com csv.DictWriter
```

| Classe | Papel | Atributos | Métodos |
|--------|-------|-----------|---------|
| `Orientacao` | um registro do JSON | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()` |
| `BaseConhecimento` | conjunto de orientações | caminho, orientacoes | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()` |
| `Assistente` | quem conversa com o cidadão | nome, base, historico | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()` |

Composição: `Assistente` → `base: BaseConhecimento` → `orientacoes: [Orientacao, ...]`.

## Regra de pontuação usada

A pergunta e os textos da base passam por `normalizar()`: minúsculas, sem acentos, sem pontuação e com um espaço no começo e no fim (para só casar **palavras inteiras**).

| Regra | Pontos |
|-------|--------|
| Cada palavra-chave da orientação que aparece na pergunta | **+3** |
| Cada palavra da pergunta (4 letras ou mais) que aparece no título | **+1** |

| Melhor orientação | Resultado |
|-------------------|-----------|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| Menos de 3 pontos | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma **lista de tuplas** `(pontos, orientacao)` da maior para a menor pontuação. O assistente mostra a melhor orientação e até duas alternativas (só as que também atingiram 3 pontos).

**Exemplo:** "Qual a multa de radar?" → orientação 9 (*Multa por excesso de velocidade*): `radar` (+3) + `multa de radar` (+3) + `multa` no título (+1) = **7 pontos, confiança ALTA**.

**Ajustes feitos pela equipe em relação ao modelo do enunciado:**

- Palavras muito comuns ("como", "para", "qual", "quando"...) **não valem o ponto do título**, para evitar que perguntas genéricas pontuem à toa. Elas continuam valendo normalmente quando fazem parte de uma palavra-chave.
- A normalização também remove `-`, `/`, aspas e `ü`, além dos sinais e acentos do enunciado.

## Regras de atendimento

- **Entradas inválidas** (letras, vazio, número fora da faixa, s/n inválido) nunca encerram o programa.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Texto com 8 ou mais dígitos ou com `@` é recusado e **não é registrado**.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** JSON ausente ou corrompido não trava o programa (mensagem de aviso; o histórico corrompido é renomeado para `.corrompido` e um novo é criado).
- Se a entrada de teclado for fechada (Ctrl+D) ou o usuário apertar Ctrl+C, o programa encerra com mensagem; o histórico já foi salvo.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: data, origem (`pergunta` ou `categoria`), pergunta, id da orientação, se encontrou, se ajudou, tentativas, tempo em segundos (`time.time()`), confiança, pontos, sessão e nota de facilidade (preenchida ao sair). Um atendimento por texto livre começa na primeira pergunta e termina quando a pessoa responde **s** ou volta com **0**; cada pergunta válida conta como uma tentativa.

Indicadores exibidos no menu 3:

- Resposta encontrada (%)
- Taxa de acerto: ajudou (%)
- Tempo médio para encontrar
- Tentativas por atendimento
- Facilidade de uso (1 a 5) — média das notas, uma por sessão
- Lista de dúvidas sem solução

O menu 4 (e a saída) exporta tudo para `data/atendimentos.csv` com `csv.DictWriter`.

## Fontes consultadas

Todas as orientações têm fonte oficial e a data em que a equipe conferiu (`verificado_em`):

- Código de Trânsito Brasileiro (Lei 9.503/1997): https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm
- Lei 14.071/2020 (pontuação, desconto e prazos): https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/L14071.htm
- Lei 13.281/2016 (celular ao volante): https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/lei/L13281.htm
- Ministério dos Transportes / Senatran (trânsito, Carteira Digital de Trânsito, Resolução Contran 819/2021): https://www.gov.br/transportes/pt-br/assuntos/transito

## Resultado do teste com usuários

> Preencher **somente com dados reais** do teste (mínimo 3 pessoas de fora da equipe e 10 atendimentos). Não registrar nomes nem dados pessoais.

| Indicador | Resultado |
|-----------|-----------|
| Pessoas testadas | 3 |
| Atendimentos | 6 |
| Resposta encontrada (%) | 83.3 |
| Taxa de acerto: ajudou (%) | 50 |
| Tempo médio para encontrar | 65.7 |
| Tentativas por atendimento | 1.7 |
| Facilidade de uso (1 a 5) | 4.5 |

**Dúvidas sem solução:** Da pra burlar o bafômetro?  Posso avançar no sinal vermelho?  Qual o valor da multa de avançar o sinal vermelho?

**Melhoria feita a partir do teste:** Nova palavra-chave e duvidas sobre: bafomêtro.

## Limitações

- A busca é por **palavras-chave inteiras**: não entende sinônimos, erros de digitação nem variações como plural/singular que não estejam na lista de palavras-chave.
- A base tem 14 orientações; assuntos fora dela retornam "não encontrei".
- Valores de multa e regras mudam com o tempo; cada orientação mostra a data de verificação. Regras de **taxas e documentos variam por estado** (Detran).
- Este assistente **não é um canal oficial** e não substitui o Detran, o órgão autuador ou um advogado.
- O tempo medido inclui o tempo de digitação da pessoa.

## Vídeo técnico

https://youtu.be/Djye6X7pX4M
