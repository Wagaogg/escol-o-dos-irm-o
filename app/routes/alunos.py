from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.aluno import Aluno
from app.models.usuario import Usuario
from app.models.professor import Professor
from datetime import datetime
import json  # <-- import único no topo

alunos_bp = Blueprint('alunos', __name__)

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
# LISTAR ALUNOS
# =========================
@alunos_bp.route("/alunos")
def listar():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    # Busca todos os alunos
    alunos = Aluno.query.all()
    
    # Se for professor, filtra pelas turmas dele
    if is_professor():
        usuario_id = session.get('usuario_id')
        professor = Professor.query.filter_by(usuario_id=usuario_id).first()
        if professor and professor.turmas_lista:
            turmas_do_professor = json.loads(professor.turmas_lista) if professor.turmas_lista else []
            turmas_do_professor = [t.strip().lower() for t in turmas_do_professor]
            alunos = [a for a in alunos if a.turma and a.turma.strip().lower() in turmas_do_professor]
        else:
            alunos = []
    
    # Busca (opcional)
    busca = request.args.get("busca", "").lower()
    if busca:
        alunos = [a for a in alunos if busca in (a.usuario.nome.lower() if a.usuario else "") or busca in a.matricula.lower()]
    
    # Prepara lista para o template (com dados do usuário)
    alunos_lista = []
    for a in alunos:
        alunos_lista.append({
            "id": a.id,
            "nome": a.usuario.nome if a.usuario else "Sem nome",
            "matricula": a.matricula,
            "turma": a.turma,
            "foto": a.usuario.foto if a.usuario else None,
            "responsaveis": json.loads(a.responsaveis) if a.responsaveis else []
        })
    
    return render_template(
        "alunos/listar.html",
        alunos=alunos_lista,
        busca=busca,
        tipo=session.get("tipo"),
        pode_editar=is_admin()
    )

# =========================
# CADASTRAR ALUNO
# =========================
@alunos_bp.route("/alunos/cadastrar")
def cadastrar():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar alunos.", "danger")
        return redirect(url_for('dashboard.index'))
    return render_template("alunos/cadastrar.html")

@alunos_bp.route("/alunos/salvar", methods=["POST"])
def salvar():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar alunos.", "danger")
        return redirect(url_for('dashboard.index'))
    
    nome = request.form.get("nome")
    matricula = request.form.get("matricula")
    data_nascimento = request.form.get("data_nascimento")
    serie = request.form.get("serie")
    turma = request.form.get("turma")
    email = request.form.get("email")
    telefone = request.form.get("telefone")
    
    # Processa responsáveis
    responsaveis = []
    nomes = request.form.getlist("resp_nome[]")
    telefones = request.form.getlist("resp_telefone[]")
    parentescos = request.form.getlist("resp_parentesco[]")
    for i in range(len(nomes)):
        if nomes[i].strip():
            responsaveis.append({
                "nome": nomes[i].strip(),
                "telefone": telefones[i].strip() if i < len(telefones) else "",
                "parentesco": parentescos[i].strip() if i < len(parentescos) else ""
            })
    
    # Cria usuário associado (se email não existir)
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        usuario = Usuario(
            nome=nome,
            email=email,
            tipo="aluno"
        )
        usuario.senha_criptografada = "temp123"  # senha temporária
        db.session.add(usuario)
        db.session.flush()
    
    # Cria aluno
    novo_aluno = Aluno(
        usuario_id=usuario.id,
        matricula=matricula,
        data_nascimento=datetime.strptime(data_nascimento, "%d/%m/%Y").date() if data_nascimento else None,
        serie=serie,
        turma=turma,
        telefone=telefone,
        responsaveis=json.dumps(responsaveis),
        notas="[]"
    )
    db.session.add(novo_aluno)
    db.session.commit()
    
    flash("Aluno cadastrado com sucesso!", "success")
    return redirect(url_for('alunos.listar'))

# =========================
# PERFIL DO ALUNO
# =========================
@alunos_bp.route("/alunos/<int:aluno_id>")
def perfil(aluno_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for('alunos.listar'))
    
    # Prepara dados para o template
    aluno_info = {
        "id": aluno.id,
        "nome": aluno.usuario.nome if aluno.usuario else "Sem nome",
        "matricula": aluno.matricula,
        "data_nascimento": aluno.data_nascimento.strftime("%d/%m/%Y") if aluno.data_nascimento else None,
        "serie": aluno.serie,
        "turma": aluno.turma,
        "email": aluno.usuario.email if aluno.usuario else None,
        "telefone": aluno.telefone,
        "foto": aluno.usuario.foto if aluno.usuario else None,
        "responsaveis": json.loads(aluno.responsaveis) if aluno.responsaveis else [],
        "notas": json.loads(aluno.notas) if aluno.notas else []
    }
    
    return render_template("alunos/perfil.html", aluno=aluno_info, pode_editar=is_admin())

# =========================
# EDITAR ALUNO
# =========================
@alunos_bp.route("/alunos/<int:aluno_id>/editar")
def editar(aluno_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem editar alunos.", "danger")
        return redirect(url_for('dashboard.index'))
    
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for('alunos.listar'))
    
    aluno_info = {
        "id": aluno.id,
        "nome": aluno.usuario.nome if aluno.usuario else "",
        "matricula": aluno.matricula,
        "data_nascimento": aluno.data_nascimento.strftime("%d/%m/%Y") if aluno.data_nascimento else None,
        "serie": aluno.serie,
        "turma": aluno.turma,
        "email": aluno.usuario.email if aluno.usuario else "",
        "telefone": aluno.telefone,
        "responsaveis": json.loads(aluno.responsaveis) if aluno.responsaveis else [],
        "foto": aluno.usuario.foto if aluno.usuario else None
    }
    
    return render_template("alunos/editar.html", aluno=aluno_info)

@alunos_bp.route("/alunos/<int:aluno_id>/atualizar", methods=["POST"])
def atualizar(aluno_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem editar alunos.", "danger")
        return redirect(url_for('dashboard.index'))
    
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for('alunos.listar'))
    
    # Atualiza dados
    aluno.matricula = request.form.get("matricula")
    data_nascimento = request.form.get("data_nascimento")
    aluno.data_nascimento = datetime.strptime(data_nascimento, "%d/%m/%Y").date() if data_nascimento else None
    aluno.serie = request.form.get("serie")
    aluno.turma = request.form.get("turma")
    aluno.telefone = request.form.get("telefone")
    
    # Atualiza usuário (nome e email)
    usuario = aluno.usuario
    if usuario:
        usuario.nome = request.form.get("nome")
        usuario.email = request.form.get("email")
    
    # Processa responsáveis
    responsaveis = []
    nomes = request.form.getlist("resp_nome[]")
    telefones = request.form.getlist("resp_telefone[]")
    parentescos = request.form.getlist("resp_parentesco[]")
    for i in range(len(nomes)):
        if nomes[i].strip():
            responsaveis.append({
                "nome": nomes[i].strip(),
                "telefone": telefones[i].strip() if i < len(telefones) else "",
                "parentesco": parentescos[i].strip() if i < len(parentescos) else ""
            })
    aluno.responsaveis = json.dumps(responsaveis)
    
    db.session.commit()
    flash("Aluno atualizado com sucesso!", "success")
    return redirect(url_for('alunos.perfil', aluno_id=aluno.id))

# =========================
# EXCLUIR ALUNO
# =========================
@alunos_bp.route("/alunos/<int:aluno_id>/excluir", methods=["POST"])
def excluir(aluno_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem excluir alunos.", "danger")
        return redirect(url_for('dashboard.index'))
    
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for('alunos.listar'))
    
    # Remove o aluno e o usuário associado
    usuario_id = aluno.usuario_id
    db.session.delete(aluno)
    if usuario_id:
        usuario = Usuario.query.get(usuario_id)
        if usuario:
            db.session.delete(usuario)
    db.session.commit()
    
    flash("Aluno excluído com sucesso!", "success")
    return redirect(url_for('alunos.listar'))