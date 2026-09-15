from app import db
from datetime import datetime

class Frequencia(db.Model):
    __tablename__ = 'frequencias'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=True)
    disciplina = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='presente')  # presente, falta, justificada
    observacao = db.Column(db.String(255), nullable=True)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    aluno = db.relationship('Aluno', backref='frequencias', lazy=True)
    professor = db.relationship('Professor', backref='frequencias', lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "aluno_id": self.aluno_id,
            "professor_id": self.professor_id,
            "disciplina": self.disciplina,
            "data": self.data.strftime("%d/%m/%Y") if self.data else None,
            "status": self.status,
            "observacao": self.observacao
        }