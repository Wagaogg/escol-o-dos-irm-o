from flask import Blueprint, render_template, session, redirect, url_for
from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.livro import Livro
from app.models.frequencia import Frequencia
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)

def is_admin():
    return session.get("tipo") in ["admin", "diretor"]

def is_staff():
    return session.get("tipo") in ["admin", "diretor", "professor"]

def is_professor():
    return session.get("tipo") == "professor"

def is_aluno():
    return session.get("tipo") == "aluno"

@dashboard_bp.route("/dashboard")
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    total_alunos = Aluno.query.count()
    total_professores = Professor.query.count()
    total_livros = Livro.query.count()
    disponiveis = Livro.query.filter(Livro.estoque > 0).count()
    
    aluno_logado = None
    if is_aluno():
        usuario_id = session.get('usuario_id')
        aluno_logado = Aluno.query.filter_by(usuario_id=usuario_id).first()
    
    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        tipo=session["tipo"],
        total_alunos=total_alunos,
        total_professores=total_professores,
        total_livros=total_livros,
        disponiveis=disponiveis,
        aluno_logado=aluno_logado
    )

# =========================
# API - ESTATÍSTICAS
# =========================
@dashboard_bp.route("/api/dashboard/estatisticas")
def api_estatisticas():
    if 'usuario_id' not in session:
        return {"error": "Não autorizado"}, 401
    
    # Empréstimos por mês (últimos 6 meses)
    hoje = datetime.now()
    meses_labels = []
    meses_dados = []
    
    for i in range(5, -1, -1):
        mes = hoje.month - i
        ano = hoje.year
        while mes <= 0:
            mes += 12
            ano -= 1
        
        meses_labels.append(f"{mes:02d}/{ano}")
        
        # Conta empréstimos feitos nesse mês
        inicio = datetime(ano, mes, 1).date()
        if mes == 12:
            fim = datetime(ano + 1, 1, 1).date()
        else:
            fim = datetime(ano, mes + 1, 1).date()
        
        count = Livro.query.filter(
            Livro.data_emprestimo >= inicio,
            Livro.data_emprestimo < fim
        ).count()
        meses_dados.append(count)
    
    return {
        "emprestimos_mes": {
            "labels": meses_labels,
            "data": meses_dados
        }
    }