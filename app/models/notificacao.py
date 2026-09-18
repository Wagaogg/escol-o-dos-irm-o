from app import db
from datetime import datetime

class Notificacao(db.Model):
    __tablename__ = 'notificacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    mensagem = db.Column(db.String(255), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(255), nullable=True)  # opcional (ex: /boletim/1)
    
    usuario = db.relationship('Usuario', backref='notificacoes', lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "mensagem": self.mensagem,
            "lida": self.lida,
            "criada_em": self.criada_em.strftime("%d/%m/%Y %H:%M") if self.criada_em else None,
            "link": self.link
        }