class Professor:
    def __init__(self, id, nome, email=None, telefone=None, materia=None, turmas=None,
                 foto=None, disciplinas=None, turmas_lista=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.materia = materia          # principal (string) - preenchido automaticamente
        self.turmas = turmas            # legado (string) - preenchido automaticamente
        self.foto = foto
        self.disciplinas = disciplinas if disciplinas is not None else []
        self.turmas_lista = turmas_lista if turmas_lista is not None else []

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "materia": self.materia,
            "turmas": self.turmas,
            "foto": self.foto,
            "disciplinas": self.disciplinas,
            "turmas_lista": self.turmas_lista
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(
            id=dados.get("id"),
            nome=dados.get("nome"),
            email=dados.get("email"),
            telefone=dados.get("telefone"),
            materia=dados.get("materia"),
            turmas=dados.get("turmas"),
            foto=dados.get("foto"),
            disciplinas=dados.get("disciplinas", []),
            turmas_lista=dados.get("turmas_lista", [])
        )