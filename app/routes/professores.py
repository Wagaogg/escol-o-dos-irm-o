from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils import carregar_professores, salvar_professores
from app.models.professor import Professor

professores_bp = Blueprint('professores', __name__)

# =========================
# PERMISSÕES
# =========================
def is_admin():
    return session.get("tipo") in ["admin", "diretor"]

def is_staff():
    return session.get("tipo") in ["admin", "diretor", "professor"]

def is_professor():
    return session.get("tipo") == "professor"

# =========================
# LISTAR PROFESSORES
# =========================
@professores_bp.route("/professores")
def listar():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.home'))
    
    professores = carregar_professores()
    busca = request.args.get("busca", "").lower()
    
    # Se for professor, vê apenas o próprio perfil
    if is_professor():
        email = session.get("email", "")
        professores = [p for p in professores if (p.email or "").lower() == email.lower()]
    else:
        if busca:
            professores = [p for p in professores if busca in p.nome.lower()]
    
    return render_template(
        "professores/listar.html",
        professores=professores,
        busca=busca,
        tipo=session.get("tipo"),
        pode_editar=is_admin()
    )

# =========================
# CADASTRAR PROFESSOR
# =========================
@professores_bp.route("/professores/cadastrar")
def cadastrar():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar professores.", "danger")
        return redirect(url_for('dashboard.home'))
    return render_template("professores/cadastrar.html")

@professores_bp.route("/professores/salvar", methods=["POST"])
def salvar():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar professores.", "danger")
        return redirect(url_for('dashboard.home'))
    
    professores = carregar_professores()
    novo_id = max([p.id for p in professores], default=0) + 1
    
    novo = Professor(
        id=novo_id,
        nome=request.form.get("nome"),
        email=request.form.get("email"),
        telefone=request.form.get("telefone"),
        materia="",
        turmas="",
        disciplinas=[],
        turmas_lista=[]
    )
    professores.append(novo)
    salvar_professores(professores)
    flash("Professor cadastrado com sucesso!", "success")
    return redirect(url_for('professores.listar'))

# =========================
# EDITAR PROFESSOR
# =========================
@professores_bp.route("/professores/<int:prof_id>/editar")
def editar(prof_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem editar professores.", "danger")
        return redirect(url_for('dashboard.home'))
    
    professores = carregar_professores()
    prof = next((p for p in professores if p.id == prof_id), None)
    if not prof:
        flash("Professor não encontrado.", "danger")
        return redirect(url_for('professores.listar'))
    
    return render_template("professores/editar.html", prof=prof)

@professores_bp.route("/professores/<int:prof_id>/atualizar", methods=["POST"])
def atualizar(prof_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem editar professores.", "danger")
        return redirect(url_for('dashboard.home'))
    
    professores = carregar_professores()
    for p in professores:
        if p.id == prof_id:
            p.nome = request.form.get("nome")
            p.email = request.form.get("email")
            p.telefone = request.form.get("telefone")
            
            disciplinas = [d.strip() for d in request.form.get("disciplinas", "").split(",") if d.strip()]
            turmas_lista = [t.strip() for t in request.form.get("turmas_lista", "").split(",") if t.strip()]
            
            p.disciplinas = disciplinas
            p.turmas_lista = turmas_lista
            p.materia = disciplinas[0] if disciplinas else ""
            p.turmas = ", ".join(turmas_lista)
            break
    
    salvar_professores(professores)
    flash("Professor atualizado com sucesso!", "success")
    return redirect(url_for('professores.listar'))

# =========================
# EXCLUIR PROFESSOR
# =========================
@professores_bp.route("/professores/<int:prof_id>/excluir", methods=["POST"])
def excluir(prof_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem excluir professores.", "danger")
        return redirect(url_for('dashboard.home'))
    
    professores = carregar_professores()
    professores = [p for p in professores if p.id != prof_id]
    salvar_professores(professores)
    flash("Professor excluído com sucesso!", "success")
    return redirect(url_for('professores.listar'))