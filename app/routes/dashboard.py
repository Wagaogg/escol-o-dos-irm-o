from flask import Blueprint, render_template, session, redirect, url_for
from app.utils import carregar_json, carregar_alunos, carregar_professores

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
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    alunos = carregar_alunos()
    professores = carregar_professores()
    livros = carregar_json("livros.json")
    
    total_alunos = len(alunos)
    total_professores = len(professores)
    total_livros = len(livros)
    disponiveis = len([l for l in livros if not l.get("emprestado", False)])
    
    aluno_logado = None
    if is_aluno():
        email = session.get("email", "")
        aluno_logado = next((a for a in alunos if (a.email or "").lower() == email.lower()), None)
    
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