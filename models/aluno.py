class Aluno:
    def __init__(self, id, nome, matricula, data_nascimento=None, serie=None, turma=None,
                 email=None, telefone=None, foto=None, notas=None, responsaveis=None):
        self.id = id
        self.nome = nome
        self.matricula = matricula
        self.data_nascimento = data_nascimento
        self.serie = serie
        self.turma = turma
        self.email = email
        self.telefone = telefone
        self.foto = foto
        self.notas = notas if notas is not None else []
        self.responsaveis = responsaveis if responsaveis is not None else []

    def adicionar_nota(self, disciplina, bimestre, nota):
        self.notas.append({
            "disciplina": disciplina,
            "bimestre": bimestre,
            "nota": nota
        })

    def obter_notas_por_disciplina(self, disciplina):
        return [n["nota"] for n in self.notas if n["disciplina"] == disciplina]

    def calcular_media_disciplina(self, disciplina):
        notas = self.obter_notas_por_disciplina(disciplina)
        if len(notas) == 4:
            return round(sum(notas) / 4, 2)
        return None

    def calcular_media_geral(self):
        disciplinas = set(n["disciplina"] for n in self.notas)
        medias = []
        for d in disciplinas:
            media = self.calcular_media_disciplina(d)
            if media is not None:
                medias.append(media)
        if not medias:
            return None
        return round(sum(medias) / len(medias), 2)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "matricula": self.matricula,
            "data_nascimento": self.data_nascimento,
            "serie": self.serie,
            "turma": self.turma,
            "email": self.email,
            "telefone": self.telefone,
            "foto": self.foto,
            "notas": self.notas,
            "responsaveis": self.responsaveis
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(
            id=dados.get("id"),
            nome=dados.get("nome"),
            matricula=dados.get("matricula"),
            data_nascimento=dados.get("data_nascimento"),
            serie=dados.get("serie"),
            turma=dados.get("turma"),
            email=dados.get("email"),
            telefone=dados.get("telefone"),
            foto=dados.get("foto"),
            notas=dados.get("notas", []),
            responsaveis=dados.get("responsaveis", [])
        )