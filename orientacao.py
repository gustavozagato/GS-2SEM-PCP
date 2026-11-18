"""Classe Orientacao: representa UM registro da base de conhecimento (um item do JSON)."""


class Orientacao:
    AVISO = "Aviso: este assistente NÃO é um canal oficial."

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):

        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @classmethod
    def de_dicionario(cls, dados):
        return cls(
            id=dados["id"],
            categoria=dados["categoria"],
            titulo=dados["titulo"],
            palavras_chave=dados["palavras_chave"],
            resposta=dados["resposta"],
            documentos=dados["documentos"],
            onde=dados["onde"],
            fonte=dados["fonte"],
            verificado_em=dados["verificado_em"],
        )

    def exibir(self):
        print(f"\n>> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários:")
        for doc in self.documentos:
            print(f"  - {doc}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(self.AVISO)
