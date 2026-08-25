class Usuario:
    def __init__(self, nome, email, senha, tipo):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo = tipo

    def to_dict(self):
        return {
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,
            "tipo": self.tipo
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(
            nome=dados.get("nome"),
            email=dados.get("email"),
            senha=dados.get("senha"),
            tipo=dados.get("tipo")
        )