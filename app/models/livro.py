from app import db
from datetime import datetime

class Livro(db.Model):
    __tablename__ = 'livros'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    editora = db.Column(db.String(200), nullable=True)
    ano = db.Column(db.String(20), nullable=True)
    genero = db.Column(db.String(50), nullable=True)
    quantidade = db.Column(db.Integer, default=1)
    estoque = db.Column(db.Integer, default=1)
    prazo_devolucao = db.Column(db.Integer, default=7)
    emprestado = db.Column(db.Boolean, default=False)
    emprestado_para = db.Column(db.String(200), nullable=True)
    data_emprestimo = db.Column(db.Date, nullable=True)
    data_devolucao = db.Column(db.Date, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "editora": self.editora,
            "ano": self.ano,
            "genero": self.genero,
            "quantidade": self.quantidade,
            "estoque": self.estoque,
            "prazo_devolucao": self.prazo_devolucao,
            "emprestado": self.emprestado,
            "emprestado_para": self.emprestado_para,
            "data_emprestimo": self.data_emprestimo.strftime("%Y-%m-%d") if self.data_emprestimo else None,
            "data_devolucao": self.data_devolucao.strftime("%Y-%m-%d") if self.data_devolucao else None
        }