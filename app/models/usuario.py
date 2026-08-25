from app import db, bcrypt
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='aluno')
    foto = db.Column(db.String(200), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos (1-1 com Aluno e Professor)
    aluno = db.relationship('Aluno', backref='usuario_rel', uselist=False, lazy=True)
    professor = db.relationship('Professor', backref='usuario_rel', uselist=False, lazy=True)
    
    @property
    def senha_criptografada(self):
        return self.senha
    
    @senha_criptografada.setter
    def senha_criptografada(self, senha_texto):
        self.senha = bcrypt.generate_password_hash(senha_texto).decode('utf-8')
    
    def verificar_senha(self, senha_texto):
        return bcrypt.check_password_hash(self.senha, senha_texto)
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tipo": self.tipo,
            "foto": self.foto,
            "criado_em": self.criado_em.strftime("%Y-%m-%d %H:%M:%S") if self.criado_em else None
        }