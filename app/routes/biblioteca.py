from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from app.utils import carregar_json, salvar_json, carregar_alunos, formatar_data_br

biblioteca_bp = Blueprint('biblioteca', __name__)

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
# BIBLIOTECA - LISTAR LIVROS
# =========================
@biblioteca_bp.route("/biblioteca")
def listar():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    livros = carregar_json("livros.json")
    busca = request.args.get("busca", "").lower()
    filtro = request.args.get("filtro", "todos")
    
    resultado = livros
    if busca:
        resultado = [l for l in resultado if busca in l["titulo"].lower() or busca in l.get("autor", "").lower()]
    if filtro == "disponivel":
        resultado = [l for l in resultado if l.get("estoque", 0) > 0]
    elif filtro == "emprestado":
        resultado = [l for l in resultado if l.get("estoque", 0) == 0]
    
    nome_aluno_logado = None
    email_aluno_logado = None
    if is_aluno():
        email = session.get("email", "")
        alunos = carregar_alunos()
        aluno = next((a for a in alunos if (a.email or "").lower() == email.lower()), None)
        if aluno:
            nome_aluno_logado = aluno.nome
            email_aluno_logado = aluno.email

    # Verifica se o aluno já tem um livro emprestado
    aluno_tem_livro = False
    if is_aluno():
        for livro in resultado:
            if livro.get("emprestado") and livro.get("emprestado_para") == session.get("usuario"):
                aluno_tem_livro = True
                break

    usuario_atual = session.get("usuario", "").strip().lower()
    email_atual = session.get("email", "").strip().lower()
    todos_alunos = carregar_alunos()

    for livro in resultado:
        emprestado_para = (livro.get("emprestado_para") or "").strip().lower()
        aluno_do_livro = next((a for a in todos_alunos if a.nome and a.nome.strip().lower() == emprestado_para), None)
        email_do_aluno = aluno_do_livro.email.lower() if aluno_do_livro and aluno_do_livro.email else ""

        livro["pode_devolver"] = (
            livro.get("emprestado") and (
                is_staff() or
                (is_aluno() and email_do_aluno == email_atual)
            )
        )
        
        livro["pode_emprestar"] = (
            livro.get("estoque", 0) > 0 and
            (is_staff() or (is_aluno() and not aluno_tem_livro))
        )
        livro["estoque_display"] = livro.get("estoque", 0)
        
        if livro.get("data_devolucao"):
            livro["data_devolucao_br"] = formatar_data_br(livro["data_devolucao"])
        else:
            livro["data_devolucao_br"] = "-"

    return render_template(
        "biblioteca/listar.html",
        livros=resultado,
        busca=busca,
        filtro=filtro,
        tipo=session.get("tipo"),
        nome_aluno_logado=nome_aluno_logado
    )

# =========================
# CADASTRAR LIVRO
# =========================
@biblioteca_bp.route("/biblioteca/cadastrar")
def cadastrar_livro():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar livros.", "danger")
        return redirect(url_for('biblioteca.listar'))
    return render_template("biblioteca/cadastrar.html")

@biblioteca_bp.route("/biblioteca/salvar", methods=["POST"])
def salvar_livro():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar livros.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    livros = carregar_json("livros.json")
    novo_id = max([l["id"] for l in livros], default=0) + 1
    
    ano = request.form.get("ano", "").strip()
    if not ano or not ano.isdigit():
        flash("Ano de publicação inválido. Use apenas números (ex: 2024).", "danger")
        return redirect(url_for('biblioteca.cadastrar_livro'))
    
    ano_int = int(ano)
    if ano_int < 1000 or ano_int > 9999:
        flash("Ano de publicação inválido. Use um ano entre 1000 e 9999.", "danger")
        return redirect(url_for('biblioteca.cadastrar_livro'))
    
    try:
        quantidade = int(request.form.get("quantidade", 1))
        if quantidade < 1:
            quantidade = 1
    except:
        quantidade = 1
    
    try:
        prazo_devolucao = int(request.form.get("prazo_devolucao", 7))
        if prazo_devolucao < 1:
            prazo_devolucao = 7
        elif prazo_devolucao > 365:
            prazo_devolucao = 365
    except:
        prazo_devolucao = 7
    
    novo = {
        "id": novo_id,
        "titulo": request.form.get("titulo"),
        "autor": request.form.get("autor"),
        "editora": request.form.get("editora"),
        "ano": str(ano_int),
        "genero": request.form.get("genero"),
        "quantidade": quantidade,
        "estoque": quantidade,
        "prazo_devolucao": prazo_devolucao,
        "emprestado": False,
        "emprestado_para": None,
        "data_emprestimo": None,
        "data_devolucao": None
    }
    livros.append(novo)
    salvar_json("livros.json", livros)
    flash(f"Livro cadastrado com sucesso! {quantidade} exemplar(es) em estoque. Prazo: {prazo_devolucao} dias.", "success")
    return redirect(url_for('biblioteca.listar'))

# =========================
# EMPRESTAR LIVRO
# =========================
@biblioteca_bp.route("/biblioteca/emprestar", methods=["POST"])
def emprestar_livro():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    livro_id = request.form.get("livro_id")
    if not livro_id:
        flash("ID do livro não informado.", "danger")
        return redirect(url_for('biblioteca.listar'))
    try:
        livro_id = int(livro_id)
    except:
        flash("ID inválido.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    nome_aluno = request.form.get("nome_aluno", "").strip()
    if not nome_aluno:
        flash("Nome do aluno é obrigatório.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    # Verifica se o aluno já tem um livro emprestado
    if is_aluno():
        email = session.get("email", "")
        alunos = carregar_alunos()
        aluno_logado = next((a for a in alunos if (a.email or "").lower() == email.lower()), None)
        if not aluno_logado:
            flash("Aluno não encontrado no sistema.", "danger")
            return redirect(url_for('biblioteca.listar'))
        
        livros = carregar_json("livros.json")
        for l in livros:
            if l.get("emprestado_para") == nome_aluno and l.get("emprestado"):
                flash(f"O aluno {nome_aluno} já possui um livro emprestado.", "danger")
                return redirect(url_for('biblioteca.listar'))
        
        nome_correto = aluno_logado.nome.strip().lower()
        nome_digitado = nome_aluno.strip().lower()
        if nome_digitado != nome_correto:
            flash("Aluno só pode emprestar livros para si mesmo.", "danger")
            return redirect(url_for('biblioteca.listar'))
    
    livros = carregar_json("livros.json")
    livro_encontrado = None
    for l in livros:
        if l["id"] == livro_id:
            livro_encontrado = l
            break
    
    if not livro_encontrado:
        flash("Livro não encontrado.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    if livro_encontrado.get("estoque", 0) <= 0:
        flash("Este livro não tem exemplares disponíveis.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    # Realiza empréstimo
    livro_encontrado["estoque"] = livro_encontrado.get("estoque", 0) - 1
    livro_encontrado["emprestado"] = True
    livro_encontrado["emprestado_para"] = nome_aluno
    livro_encontrado["data_emprestimo"] = datetime.now().strftime("%Y-%m-%d")
    
    try:
        prazo_dias = livro_encontrado.get("prazo_devolucao", 7)
        prazo_dias = int(prazo_dias)
        if prazo_dias < 1:
            prazo_dias = 1
        elif prazo_dias > 365:
            prazo_dias = 365
    except (ValueError, TypeError):
        prazo_dias = 7
    
    data_devolucao = datetime.now() + timedelta(days=prazo_dias)
    livro_encontrado["data_devolucao"] = data_devolucao.strftime("%Y-%m-%d")
    
    salvar_json("livros.json", livros)
    data_br = data_devolucao.strftime("%d/%m/%Y")
    flash(f"Empréstimo realizado! {livro_encontrado['titulo']} - Devolver até: {data_br}.", "success")
    return redirect(url_for('biblioteca.listar'))

# =========================
# DEVOLVER LIVRO
# =========================
@biblioteca_bp.route("/biblioteca/<int:livro_id>/devolver", methods=["POST"])
def devolver_livro(livro_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    livros = carregar_json("livros.json")
    livro = next((l for l in livros if l["id"] == livro_id), None)
    if not livro:
        flash("Livro não encontrado.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    if not livro.get("emprestado"):
        flash("Este livro não está emprestado.", "warning")
        return redirect(url_for('biblioteca.listar'))
    
    email_atual = session.get("email", "").strip().lower()
    emprestado_para = (livro.get("emprestado_para") or "").strip().lower()
    
    todos_alunos = carregar_alunos()
    aluno_do_livro = next((a for a in todos_alunos if a.nome and a.nome.strip().lower() == emprestado_para), None)
    email_do_aluno = aluno_do_livro.email.lower() if aluno_do_livro and aluno_do_livro.email else ""

    pode_devolver = False
    if is_staff():
        pode_devolver = True
    elif is_aluno() and email_do_aluno == email_atual:
        pode_devolver = True
    
    if pode_devolver:
        livro["emprestado"] = False
        livro["emprestado_para"] = None
        livro["data_emprestimo"] = None
        livro["data_devolucao"] = None
        livro["estoque"] = livro.get("estoque", 0) + 1
        salvar_json("livros.json", livros)
        flash(f"Livro devolvido com sucesso! Estoque atual: {livro['estoque']} exemplar(es).", "success")
    else:
        flash("Você não tem permissão para devolver este livro.", "danger")
    
    return redirect(url_for('biblioteca.listar'))

# =========================
# EXCLUIR LIVRO
# =========================
@biblioteca_bp.route("/biblioteca/<int:livro_id>/excluir", methods=["POST"])
def excluir_livro(livro_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem excluir livros.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    livros = carregar_json("livros.json")
    livros = [l for l in livros if l["id"] != livro_id]
    salvar_json("livros.json", livros)
    flash("Livro excluído com sucesso.", "success")
    return redirect(url_for('biblioteca.listar'))