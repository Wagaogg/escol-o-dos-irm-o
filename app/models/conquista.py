from app import db
from datetime import datetime


class Conquista(db.Model):
    __tablename__ = 'conquistas'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    desbloqueada_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', backref='conquistas', lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "codigo": self.codigo,
            "desbloqueada_em": self.desbloqueada_em.strftime("%d/%m/%Y") if self.desbloqueada_em else None
        }


class ConquistaVista(db.Model):
    """Controla quais toasts já foram vistos pelo usuário"""
    __tablename__ = 'conquistas_vistas'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    conquista_id = db.Column(db.Integer, db.ForeignKey('conquistas.id'), nullable=False)
    vista_em = db.Column(db.DateTime, default=datetime.utcnow)