from flask import Blueprint, render_template, session, redirect, url_for
from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.livro import Livro
from app.models.frequencia import Frequencia

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

    # 🔥 Dispatcher: verifica conquistas conforme o tipo
    try:
        from app.routes.conquistas import verificar_conquistas
        verificar_conquistas(session.get('usuario_id'))
    except Exception as e:
        print(f"Erro ao verificar conquistas: {e}")

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


@dashboard_bp.route("/api/dashboard/estatisticas")
def api_estatisticas():
    if 'usuario_id' not in session:
        return {"error": "Não autorizado"}, 401

    livros = Livro.query.all()
    top_livros = []
    for l in livros:
        emprestados = l.quantidade - l.estoque
        if emprestados > 0:
            top_livros.append({"label": l.titulo, "value": emprestados})
    top_livros = sorted(top_livros, key=lambda x: x["value"], reverse=True)[:5]

    total_presente = Frequencia.query.filter_by(status="presente").count()
    total_falta = Frequencia.query.filter_by(status="falta").count()
    total_justificada = Frequencia.query.filter_by(status="justificada").count()

    return {
        "top_livros": top_livros,
        "frequencia": {
            "presente": total_presente,
            "falta": total_falta,
            "justificada": total_justificada
        }
    }