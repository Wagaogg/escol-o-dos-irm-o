from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.professor import Professor
from app.models.usuario import Usuario
import json

professores_bp = Blueprint('professores', __name__)

def is_admin():
    return session.get("tipo") in ["admin", "diretor"]

def is_staff():
    return session.get("tipo") in ["admin", "diretor", "professor"]

def is_professor():
    return session.get("tipo") == "professor"

@professores_bp.route("/professores")
def listar():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    professores = Professor.query.all()
    
    if is_professor():
        usuario_id = session.get('usuario_id')
        professor = Professor.query.filter_by(usuario_id=usuario_id).first()
        if professor:
            professores = [professor]
        else:
            professores = []
    
    busca = request.args.get("busca", "").lower()
    if busca:
        professores = [p for p in professores if busca in (p.usuario.nome.lower() if p.usuario else "")]
    
    professores_lista = []
    for p in professores:
        professores_lista.append({
            "id": p.id,
            "nome": p.usuario.nome if p.usuario else "Sem nome",
            "email": p.email or (p.usuario.email if p.usuario else ""),
            "telefone": p.telefone or "",
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
    
    # Verifica se já existe um professor com esse email
    prof_existente = Professor.query.filter(
        db.func.lower(Professor.email) == email.lower()
    ).first()
    if prof_existente:
        flash("Já existe um professor cadastrado com este email.", "danger")
        return redirect(url_for('professores.cadastrar'))
    
    # Verifica se já existe um usuário com esse email
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        # Já existe usuário → vincula
        usuario.tipo = "professor"
        usuario.nome = nome
        db.session.commit()
        usuario_id = usuario.id
    else:
        # Não existe usuário → deixa como NULL (será criado quando ele se cadastrar)
        usuario_id = None
    
    novo_professor = Professor(
        usuario_id=usuario_id,
        email=email,
        materia="",
        turmas="",
        disciplinas="[]",
        turmas_lista="[]",
        telefone=telefone
    )
    db.session.add(novo_professor)
    db.session.commit()
    
    flash("Professor cadastrado com sucesso!", "success")
    return redirect(url_for('professores.listar'))

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
        "email": professor.email or (professor.usuario.email if professor.usuario else ""),
        "telefone": professor.telefone or "",
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
    
    professor.materia = request.form.get("materia")
    professor.telefone = request.form.get("telefone")
    professor.email = request.form.get("email")  # atualiza email
    
    disciplinas = request.form.get("disciplinas", "")
    turmas_lista = request.form.get("turmas_lista", "")
    
    professor.disciplinas = json.dumps([d.strip() for d in disciplinas.split(",") if d.strip()])
    professor.turmas_lista = json.dumps([t.strip() for t in turmas_lista.split(",") if t.strip()])
    professor.turmas = turmas_lista
    
    usuario = professor.usuario
    if usuario:
        usuario.nome = request.form.get("nome")
        usuario.email = request.form.get("email")
    
    db.session.commit()
    flash("Professor atualizado com sucesso!", "success")
    return redirect(url_for('professores.listar'))

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
    
    db.session.delete(professor)
    db.session.commit()
    
    flash("Professor excluído com sucesso!", "success")
    return redirect(url_for('professores.listar'))