from app import db
import json

class Professor(db.Model):
    __tablename__ = 'professores'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)  # NOVO CAMPO
    materia = db.Column(db.String(100), nullable=True)
    turmas = db.Column(db.String(200), nullable=True)
    disciplinas = db.Column(db.Text, nullable=True)
    turmas_lista = db.Column(db.Text, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    
    usuario = db.relationship('Usuario', backref='professor_rel', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "email": self.email or (self.usuario.email if self.usuario else None),
            "nome": self.usuario.nome if self.usuario else None,
            "materia": self.materia,
            "turmas": self.turmas,
            "disciplinas": json.loads(self.disciplinas) if self.disciplinas else [],
            "turmas_lista": json.loads(self.turmas_lista) if self.turmas_lista else [],
            "telefone": self.telefone,
            "foto": self.usuario.foto if self.usuario else None
        }