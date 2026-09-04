from flask import Blueprint, render_template, session, redirect, url_for
from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.livro import Livro

dashboard_bp = Blueprint('dashboard', __name__)

# =========================
# PERMISSÕES
# =========================
def is_admin():
    return session.get("tipo") in ["admin", "diretor"]

def is_staff():
    return session.get("tipo") in ["admin", "diretor", "professor"]

def is_professor():
    return session.get("tipo") == "professor"

def is_aluno():
    return session.get("tipo") == "aluno"

# =========================
# DASHBOARD
# =========================
@dashboard_bp.route("/dashboard")
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Consultas ao SQLite
    total_alunos = Aluno.query.count()
    total_professores = Professor.query.count()
    livros = Livro.query.all()
    total_livros = len(livros)
    disponiveis = sum(1 for l in livros if l.estoque > 0)
    
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