from app import db
from datetime import datetime

class Aluno(db.Model):
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    serie = db.Column(db.String(20), nullable=True)
    turma = db.Column(db.String(20), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    responsaveis = db.Column(db.Text, nullable=True)  # JSON string
    notas = db.Column(db.Text, nullable=True)  # JSON string
    
    usuario = db.relationship('Usuario', backref='aluno_rel', uselist=False, lazy=True)
    
    def to_dict(self):
        import json
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "nome": self.usuario.nome if self.usuario else None,
            "email": self.usuario.email if self.usuario else None,
            "matricula": self.matricula,
            "data_nascimento": self.data_nascimento.strftime("%d/%m/%Y") if self.data_nascimento else None,
            "serie": self.serie,
            "turma": self.turma,
            "telefone": self.telefone,
            "responsaveis": json.loads(self.responsaveis) if self.responsaveis else [],
            "notas": json.loads(self.notas) if self.notas else [],
            "foto": self.usuario.foto if self.usuario else None
        }