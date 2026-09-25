from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.aluno import Aluno
from app.models.usuario import Usuario
from app.models.professor import Professor
from datetime import datetime
import json
import re

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
# NORMALIZAR TURMA
# =========================
def normalizar(texto):
    """Remove TUDO que não for letra ou número e converte pra minúsculo.
    Ex: '99° roblox' → '99roblox'
        '99º roblox' → '99roblox'
        '3A' → '3a'
    """
    if not texto:
        return ""
    texto = str(texto).lower()
    texto = re.sub(r'[^a-z0-9]', '', texto)
    return texto

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
    
    alunos = Aluno.query.all()
    
    # 🔥 Se for professor, filtra apenas os alunos das turmas dele
    if is_professor():
        usuario_id = session.get('usuario_id')
        professor = Professor.query.filter_by(usuario_id=usuario_id).first()
        
        if professor and professor.turmas_lista:
            try:
                turmas_do_professor = json.loads(professor.turmas_lista)
            except:
                turmas_do_professor = []
            
            turmas_norm = [normalizar(t) for t in turmas_do_professor if t]
            
            print(f"🔍 Professor: {professor.usuario.nome if professor.usuario else '?'}")
            print(f"🔍 Turmas do professor: {turmas_do_professor}")
            print(f"🔍 Turmas normalizadas: {turmas_norm}")
            
            alunos_filtrados = []
            for a in alunos:
                if a.turma:
                    turma_norm = normalizar(a.turma)
                    match = turma_norm in turmas_norm
                    print(f"   Aluno: {a.usuario.nome if a.usuario else '?'} | Turma: '{a.turma}' | Normalizada: '{turma_norm}' | Match: {match}")
                    if match:
                        alunos_filtrados.append(a)
            
            alunos = alunos_filtrados
        else:
            print("⚠️ Professor sem turmas cadastradas.")
            alunos = []
    
    # Busca (opcional)
    busca = request.args.get("busca", "").lower()
    if busca:
        alunos = [
            a for a in alunos
            if busca in (a.usuario.nome.lower() if a.usuario else "")
            or busca in (a.matricula or "").lower()
        ]
    
    # Prepara lista pra o template
    alunos_lista = []
    for a in alunos:
        alunos_lista.append({
            "id": a.id,
            "nome": a.usuario.nome if a.usuario else "Sem nome",
            "matricula": a.matricula,
            "turma": a.turma,
            "serie": a.serie,
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
    
    # Cria usuário associado
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        usuario = Usuario(nome=nome, email=email, tipo="aluno")
        usuario.senha_criptografada = "temp123"
        db.session.add(usuario)
        db.session.flush()
    
    # Converte data
    data_obj = None
    if data_nascimento:
        try:
            data_obj = datetime.strptime(data_nascimento, "%d/%m/%Y").date()
        except:
            try:
                data_obj = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
            except:
                data_obj = None
    
    novo_aluno = Aluno(
        usuario_id=usuario.id,
        matricula=matricula,
        data_nascimento=data_obj,
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
        "data_nascimento": aluno.data_nascimento.strftime("%d/%m/%Y") if aluno.data_nascimento else "",
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
    
    aluno.matricula = request.form.get("matricula")
    aluno.serie = request.form.get("serie")
    aluno.turma = request.form.get("turma")
    aluno.telefone = request.form.get("telefone")
    
    data_nascimento = request.form.get("data_nascimento")
    if data_nascimento:
        try:
            aluno.data_nascimento = datetime.strptime(data_nascimento, "%d/%m/%Y").date()
        except:
            pass
    
    usuario = aluno.usuario
    if usuario:
        usuario.nome = request.form.get("nome")
        usuario.email = request.form.get("email")
    
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
    
    db.session.delete(aluno)
    db.session.commit()
    flash("Aluno excluído com sucesso!", "success")
    return redirect(url_for('alunos.listar'))