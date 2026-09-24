from app import db
from datetime import datetime

class Configuracao(db.Model):
    __tablename__ = 'configuracoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    
    # Aparência
    tema = db.Column(db.String(20), default='escuro')          # escuro, claro
    cor_destaque = db.Column(db.String(20), default='#5865F2') # HEX
    densidade = db.Column(db.String(20), default='confortavel')# compacto, confortavel
    sidebar_recolhida = db.Column(db.Boolean, default=False)
    fonte = db.Column(db.String(30), default='Inter')          # Inter, Roboto, System
    tamanho_fonte = db.Column(db.Integer, default=15)          # 13 a 18
    
    # Notificações
    notif_emprestimo = db.Column(db.Boolean, default=True)
    notif_nota = db.Column(db.Boolean, default=True)
    notif_falta = db.Column(db.Boolean, default=True)
    
    # Privacidade
    perfil_publico = db.Column(db.Boolean, default=False)
    
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    usuario = db.relationship('Usuario', backref='configuracao', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            "tema": self.tema,
            "cor_destaque": self.cor_destaque,
            "densidade": self.densidade,
            "sidebar_recolhida": self.sidebar_recolhida,
            "fonte": self.fonte,
            "tamanho_fonte": self.tamanho_fonte,
            "notif_emprestimo": self.notif_emprestimo,
            "notif_nota": self.notif_nota,
            "notif_falta": self.notif_falta,
            "perfil_publico": self.perfil_publico,
        }