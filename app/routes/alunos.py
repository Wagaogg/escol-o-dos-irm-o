from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils import carregar_alunos, salvar_alunos, carregar_professores, formatar_data_br
from app.models.aluno import Aluno

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

def is_aluno():
    return session.get("tipo") == "aluno"

# =========================
# LISTAR ALUNOS
# =========================
@alunos_bp.route("/alunos")
def listar():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.home'))
    
    alunos = carregar_alunos()
    busca = request.args.get("busca", "").lower()
    
    # Se for professor, filtra apenas os alunos das turmas dele
    if is_professor():
        email = session.get("email", "")
        professores = carregar_professores()
        professor = next((p for p in professores if (p.email or "").lower() == email.lower()), None)
        if professor and professor.turmas_lista:
            turmas_do_professor = [t.strip().lower() for t in professor.turmas_lista]
            alunos = [a for a in alunos if a.turma and a.turma.strip().lower() in turmas_do_professor]
        else:
            alunos = []
    
    if busca:
        resultado = [a for a in alunos if busca in a.nome.lower() or busca in (a.matricula or "").lower()]
    else:
        resultado = alunos
    
    return render_template(
        "alunos/listar.html",
        alunos=resultado,
        busca=busca,
        tipo=session.get("tipo"),
        pode_editar=is_admin()
    )

# =========================
# CADASTRAR ALUNO
# =========================
@alunos_bp.route("/alunos/cadastrar")
def cadastrar():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar alunos.", "danger")
        return redirect(url_for('dashboard.home'))
    return render_template("alunos/cadastrar.html")

@alunos_bp.route("/alunos/salvar", methods=["POST"])
def salvar():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar alunos.", "danger")
        return redirect(url_for('dashboard.home'))
    
    alunos = carregar_alunos()
    novo_id = max([a.id for a in alunos], default=0) + 1
    
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
    
    novo = Aluno(
        id=novo_id,
        nome=request.form.get("nome"),
        matricula=request.form.get("matricula"),
        data_nascimento=request.form.get("data_nascimento"),
        serie=request.form.get("serie"),
        turma=request.form.get("turma"),
        email=request.form.get("email"),
        telefone=request.form.get("telefone"),
        responsaveis=responsaveis
    )
    alunos.append(novo)
    salvar_alunos(alunos)
    flash("Aluno cadastrado com sucesso!", "success")
    return redirect(url_for('alunos.listar'))

# =========================
# PERFIL DO ALUNO
# =========================
@alunos_bp.route("/alunos/<int:aluno_id>")
def perfil(aluno_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.home'))
    
    alunos = carregar_alunos()
    aluno = next((a for a in alunos if a.id == aluno_id), None)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for('alunos.listar'))
    
    return render_template("alunos/perfil.html", aluno=aluno, pode_editar=is_admin())

# =========================
# EDITAR ALUNO
# =========================
@alunos_bp.route("/alunos/<int:aluno_id>/editar")
def editar(aluno_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem editar alunos.", "danger")
        return redirect(url_for('dashboard.home'))
    
    alunos = carregar_alunos()
    aluno = next((a for a in alunos if a.id == aluno_id), None)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for('alunos.listar'))
    
    if aluno.data_nascimento:
        aluno.data_nascimento = formatar_data_br(aluno.data_nascimento)
    
    return render_template("alunos/editar.html", aluno=aluno)

@alunos_bp.route("/alunos/<int:aluno_id>/atualizar", methods=["POST"])
def atualizar(aluno_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem editar alunos.", "danger")
        return redirect(url_for('dashboard.home'))
    
    alunos = carregar_alunos()
    for a in alunos:
        if a.id == aluno_id:
            a.nome = request.form.get("nome")
            a.matricula = request.form.get("matricula")
            a.data_nascimento = request.form.get("data_nascimento")
            a.serie = request.form.get("serie")
            a.turma = request.form.get("turma")
            a.email = request.form.get("email")
            a.telefone = request.form.get("telefone")
            
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
            a.responsaveis = responsaveis
            break
    
    salvar_alunos(alunos)
    flash("Aluno atualizado com sucesso!", "success")
    return redirect(url_for('alunos.perfil', aluno_id=aluno_id))

# =========================
# EXCLUIR ALUNO
# =========================
@alunos_bp.route("/alunos/<int:aluno_id>/excluir", methods=["POST"])
def excluir(aluno_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem excluir alunos.", "danger")
        return redirect(url_for('dashboard.home'))
    
    alunos = carregar_alunos()
    alunos = [a for a in alunos if a.id != aluno_id]
    salvar_alunos(alunos)
    flash("Aluno excluído com sucesso!", "success")
    return redirect(url_for('alunos.listar'))