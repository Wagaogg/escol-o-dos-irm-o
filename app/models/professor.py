from app import db
import json

class Professor(db.Model):
    __tablename__ = 'professores'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    materia = db.Column(db.String(100), nullable=True)
    turmas = db.Column(db.String(200), nullable=True)
    disciplinas = db.Column(db.Text, nullable=True)  # JSON string
    turmas_lista = db.Column(db.Text, nullable=True)  # JSON string
    
    usuario = db.relationship('Usuario', backref='professor_rel', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "nome": self.usuario.nome if self.usuario else None,
            "email": self.usuario.email if self.usuario else None,
            "materia": self.materia,
            "turmas": self.turmas,
            "disciplinas": json.loads(self.disciplinas) if self.disciplinas else [],
            "turmas_lista": json.loads(self.turmas_lista) if self.turmas_lista else [],
            "foto": self.usuario.foto if self.usuario else None
        }