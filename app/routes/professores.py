from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.professor import Professor
from app.models.usuario import Usuario
import json

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
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    # Busca todos os professores
    professores = Professor.query.all()
    
    # Se for professor, vê apenas o próprio perfil
    if is_professor():
        usuario_id = session.get('usuario_id')
        professor = Professor.query.filter_by(usuario_id=usuario_id).first()
        if professor:
            professores = [professor]
        else:
            professores = []
    
    # Busca (opcional)
    busca = request.args.get("busca", "").lower()
    if busca:
        professores = [p for p in professores if busca in (p.usuario.nome.lower() if p.usuario else "")]
    
    # Prepara lista para o template
    professores_lista = []
    for p in professores:
        professores_lista.append({
            "id": p.id,
            "nome": p.usuario.nome if p.usuario else "Sem nome",
            "email": p.usuario.email if p.usuario else "",
            "materia": p.materia,
            "turmas": p.turmas,
            "disciplinas": json.loads(p.disciplinas) if p.disciplinas else [],
            "turmas_lista": json.loads(p.turmas_lista) if p.turmas_lista else [],
            "foto": p.usuario.foto if p.usuario else None
        })
    
    return render_template(
        "professores/listar.html",
        professores=professores_lista,
        busca=busca,
        tipo=session.get("tipo"),
        pode_editar=is_admin()
    )

# =========================
# CADASTRAR PROFESSOR
# =========================
@professores_bp.route("/professores/cadastrar")
def cadastrar():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar professores.", "danger")
        return redirect(url_for('dashboard.index'))
    return render_template("professores/cadastrar.html")

@professores_bp.route("/professores/salvar", methods=["POST"])
def salvar():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar professores.", "danger")
        return redirect(url_for('dashboard.index'))
    
    nome = request.form.get("nome")
    email = request.form.get("email")
    telefone = request.form.get("telefone")
    
    # Verifica se email já existe
    if email:
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash("Este email já está em uso.", "danger")
            return redirect(url_for('professores.cadastrar'))
    
    # Cria usuário
    usuario = Usuario(
        nome=nome,
        email=email,
        tipo="professor"
    )
    usuario.senha_criptografada = "temp123"  # senha temporária
    db.session.add(usuario)
    db.session.flush()
    
    # Cria professor
    novo_professor = Professor(
        usuario_id=usuario.id,
        materia="",
        turmas="",
        disciplinas="[]",
        turmas_lista="[]"
    )
    db.session.add(novo_professor)
    db.session.commit()
    
    flash("Professor cadastrado com sucesso!", "success")
    return redirect(url_for('professores.listar'))

# =========================
# EDITAR PROFESSOR
# =========================
@professores_bp.route("/professores/<int:prof_id>/editar")
def editar(prof_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem editar professores.", "danger")
        return redirect(url_for('dashboard.index'))
    
    professor = Professor.query.get(prof_id)
    if not professor:
        flash("Professor não encontrado.", "danger")
        return redirect(url_for('professores.listar'))
    
    professor_info = {
        "id": professor.id,
        "nome": professor.usuario.nome if professor.usuario else "",
        "email": professor.usuario.email if professor.usuario else "",
        "telefone": professor.usuario.telefone if professor.usuario else "",
        "materia": professor.materia,
        "turmas": professor.turmas,
        "disciplinas": json.loads(professor.disciplinas) if professor.disciplinas else [],
        "turmas_lista": json.loads(professor.turmas_lista) if professor.turmas_lista else [],
        "foto": professor.usuario.foto if professor.usuario else None
    }
    
    return render_template("professores/editar.html", prof=professor_info)

@professores_bp.route("/professores/<int:prof_id>/atualizar", methods=["POST"])
def atualizar(prof_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem editar professores.", "danger")
        return redirect(url_for('dashboard.index'))
    
    professor = Professor.query.get(prof_id)
    if not professor:
        flash("Professor não encontrado.", "danger")
        return redirect(url_for('professores.listar'))
    
    # Atualiza dados do professor
    professor.materia = request.form.get("materia")
    
    disciplinas = request.form.get("disciplinas", "")
    turmas_lista = request.form.get("turmas_lista", "")
    
    professor.disciplinas = json.dumps([d.strip() for d in disciplinas.split(",") if d.strip()])
    professor.turmas_lista = json.dumps([t.strip() for t in turmas_lista.split(",") if t.strip()])
    
    # Atualiza campos legados (string)
    professor.turmas = turmas_lista
    
    # Atualiza usuário
    usuario = professor.usuario
    if usuario:
        usuario.nome = request.form.get("nome")
        usuario.email = request.form.get("email")
        usuario.telefone = request.form.get("telefone")
    
    db.session.commit()
    flash("Professor atualizado com sucesso!", "success")
    return redirect(url_for('professores.listar'))

# =========================
# EXCLUIR PROFESSOR
# =========================
@professores_bp.route("/professores/<int:prof_id>/excluir", methods=["POST"])
def excluir(prof_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem excluir professores.", "danger")
        return redirect(url_for('dashboard.index'))
    
    professor = Professor.query.get(prof_id)
    if not professor:
        flash("Professor não encontrado.", "danger")
        return redirect(url_for('professores.listar'))
    
    usuario_id = professor.usuario_id
    db.session.delete(professor)
    if usuario_id:
        usuario = Usuario.query.get(usuario_id)
        if usuario:
            db.session.delete(usuario)
    db.session.commit()
    
    flash("Professor excluído com sucesso!", "success")
    return redirect(url_for('professores.listar'))