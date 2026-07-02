from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

# Importar os modelos (assumindo que estão em models/)
from models.aluno import Aluno
from models.professor import Professor
from models.usuario import Usuario

app = Flask(__name__)
app.secret_key = "sistema_escolar_2026"

# ====== DEFINIÇÕES DE PASTAS ======
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =========================
# UTILITÁRIOS
# =========================

def formatar_data_br(data_str):
    """Converte data ISO (yyyy-mm-dd) para formato brasileiro (dd/mm/yyyy)"""
    if not data_str:
        return None
    try:
        # Se já estiver no formato br (dd/mm/yyyy), retorna
        if '/' in data_str:
            return data_str
        # Converte ISO para br
        data_obj = datetime.strptime(data_str, "%Y-%m-%d")
        return data_obj.strftime("%d/%m/%Y")
    except:
        return data_str

# =========================
# CARREGAR / SALVAR DADOS
# =========================

def carregar_json(arquivo, padrao=None):
    if padrao is None:
        padrao = []
    caminho = os.path.join(DATA_DIR, arquivo)
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return list(padrao)

def salvar_json(arquivo, dados):
    caminho = os.path.join(DATA_DIR, arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- Alunos ---
def carregar_alunos():
    dados = carregar_json("alunos.json")
    return [Aluno.from_dict(a) for a in dados]

def salvar_alunos(alunos):
    dados = [a.to_dict() for a in alunos]
    salvar_json("alunos.json", dados)

# --- Professores ---
def carregar_professores():
    dados = carregar_json("professores.json")
    return [Professor.from_dict(p) for p in dados]

def salvar_professores(professores):
    dados = [p.to_dict() for p in professores]
    salvar_json("professores.json", dados)

# --- Usuários ---
def carregar_usuarios():
    dados = carregar_json("usuarios.json")
    return [Usuario.from_dict(u) for u in dados]

def salvar_usuarios(usuarios):
    dados = [u.to_dict() for u in usuarios]
    salvar_json("usuarios.json", dados)

# =========================
# PERMISSÕES
# =========================

def requer_login():
    return "usuario" not in session

def is_admin():
    return session.get("tipo") in ["admin", "diretor"]

def is_staff():
    return session.get("tipo") in ["admin", "diretor", "professor"]

def is_professor():
    return session.get("tipo") == "professor"

def is_aluno():
    return session.get("tipo") == "aluno"

# =========================
# HOME
# =========================

@app.route("/")
def home():
    if requer_login():
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))

# =========================
# LOGIN
# =========================

@app.route("/login")
def login():
    erro = request.args.get("erro")
    return render_template("auth/login.html", erro=erro)

@app.route("/autenticar", methods=["POST"])
def autenticar():
    email = request.form.get("email")
    senha = request.form.get("senha")
    usuarios = carregar_usuarios()
    for usuario in usuarios:
        if usuario.email == email and usuario.senha == senha:
            session["usuario"] = usuario.nome
            session["tipo"]    = usuario.tipo
            session["email"]   = usuario.email
            return redirect(url_for("dashboard"))
    return redirect(url_for("login", erro=1))

# =========================
# CADASTRO DE USUÁRIO (público - todos viram aluno)
# =========================

@app.route("/cadastro")
def cadastro():
    return render_template("auth/cadastro.html", erro=0)

@app.route("/criar_conta", methods=["POST"])
def criar_conta():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    tipo = "aluno"  # sempre aluno
    
    usuarios = carregar_usuarios()
    for u in usuarios:
        if u.email == email:
            flash("Este email já está em uso.", "danger")
            return render_template("auth/cadastro.html", erro=1)
    
    # Cria usuário
    novo_usuario = Usuario(nome, email, senha, tipo)
    usuarios.append(novo_usuario)
    salvar_usuarios(usuarios)
    
    # 🔥 CRIA ALUNO automaticamente
    alunos = carregar_alunos()
    novo_id = max([a.id for a in alunos], default=0) + 1
    novo_aluno = Aluno(
        id=novo_id,
        nome=nome,
        matricula=f"MAT{novo_id:04d}",  # matrícula automática
        email=email,
        responsaveis=[]
    )
    alunos.append(novo_aluno)
    salvar_alunos(alunos)
    
    flash("Conta criada com sucesso! Faça login.", "success")
    return redirect(url_for("login"))

# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():
    if requer_login():
        return redirect(url_for("login"))
    
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

# =========================
# PERFIL DO USUÁRIO
# =========================

@app.route("/meu_perfil")
def meu_perfil():
    if requer_login():
        return redirect(url_for("login"))
    
    if is_aluno():
        alunos = carregar_alunos()
        email = session.get("email", "")
        aluno = next((a for a in alunos if (a.email or "").lower() == email.lower()), None)
        if not aluno:
            aluno = Aluno(
                id=None,
                nome=session.get("usuario"),
                email=session.get("email"),
                matricula=None,
                turma=None,
                serie=None,
                data_nascimento=None,
                telefone=None
            )
        livros = carregar_json("livros.json")
        livros_emprestados = [
            l for l in livros
            if l.get("emprestado") and (l.get("emprestado_para") or "").strip().lower() == (aluno.nome or "").strip().lower()
        ]
        return render_template("alunos/meu_perfil.html", usuario=session["usuario"], tipo=session["tipo"], aluno=aluno, livros_emprestados=livros_emprestados, foto=aluno.foto)
    
    elif is_professor():
        professores = carregar_professores()
        email = session.get("email", "")
        professor = next((p for p in professores if (p.email or "").lower() == email.lower()), None)
        if not professor:
            professor = Professor(
                id=None,
                nome=session.get("usuario"),
                email=session.get("email"),
                materia=None,
                turmas=None,
                telefone=None
            )
        return render_template("professores/meu_perfil.html", usuario=session["usuario"], tipo=session["tipo"], professor=professor, foto=professor.foto)
    else:
        return redirect(url_for("dashboard"))

# =========================
# ALUNOS (CRUD)
# =========================

@app.route("/alunos")
def alunos_lista():
    if requer_login():
        return redirect(url_for("login"))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for("dashboard"))
    
    alunos = carregar_alunos()
    busca = request.args.get("busca", "").lower()
    
    # 🔥 Se for professor, filtra apenas os alunos das turmas dele
    if is_professor():
        email = session.get("email", "")
        professores = carregar_professores()
        professor = next((p for p in professores if (p.email or "").lower() == email.lower()), None)
        if professor and professor.turmas_lista:
            turmas_do_professor = [t.strip().lower() for t in professor.turmas_lista]
            alunos = [a for a in alunos if a.turma and a.turma.strip().lower() in turmas_do_professor]
        else:
            alunos = []  # professor sem turmas não vê nenhum aluno
    
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

@app.route("/alunos/cadastrar")
def cadastrar_aluno():
    if not is_admin():
        flash("Apenas administradores podem cadastrar alunos.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("alunos/cadastrar.html")

@app.route("/alunos/salvar", methods=["POST"])
def salvar_aluno():
    if not is_admin():
        flash("Apenas administradores podem cadastrar alunos.", "danger")
        return redirect(url_for("dashboard"))
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
    return redirect(url_for("alunos_lista"))

@app.route("/alunos/<int:aluno_id>")
def perfil_aluno(aluno_id):
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for("dashboard"))
    alunos = carregar_alunos()
    aluno = next((a for a in alunos if a.id == aluno_id), None)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for("alunos_lista"))
    return render_template("alunos/perfil.html", aluno=aluno, pode_editar=is_admin())

@app.route("/alunos/<int:aluno_id>/editar")
def editar_aluno(aluno_id):
    if not is_admin():
        flash("Apenas administradores podem editar alunos.", "danger")
        return redirect(url_for("dashboard"))
    alunos = carregar_alunos()
    aluno = next((a for a in alunos if a.id == aluno_id), None)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for("alunos_lista"))
    return render_template("alunos/editar.html", aluno=aluno)

@app.route("/alunos/<int:aluno_id>/atualizar", methods=["POST"])
def atualizar_aluno(aluno_id):
    if not is_admin():
        flash("Apenas administradores podem editar alunos.", "danger")
        return redirect(url_for("dashboard"))
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
    return redirect(url_for("perfil_aluno", aluno_id=aluno_id))

@app.route("/alunos/<int:aluno_id>/excluir", methods=["POST"])
def excluir_aluno(aluno_id):
    if not is_admin():
        flash("Apenas administradores podem excluir alunos.", "danger")
        return redirect(url_for("dashboard"))
    alunos = carregar_alunos()
    alunos = [a for a in alunos if a.id != aluno_id]
    salvar_alunos(alunos)
    flash("Aluno excluído com sucesso!", "success")
    return redirect(url_for("alunos_lista"))

# =========================
# PROFESSORES (CRUD)
# =========================

@app.route("/professores")
def professores():
    if requer_login():
        return redirect(url_for("login"))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for("dashboard"))
    
    professores = carregar_professores()
    busca = request.args.get("busca", "").lower()
    
    # 🔥 Se for professor, vê apenas o próprio perfil
    if is_professor():
        email = session.get("email", "")
        professores = [p for p in professores if (p.email or "").lower() == email.lower()]
    else:
        # admin/diretor vê todos
        if busca:
            professores = [p for p in professores if busca in p.nome.lower()]
    
    return render_template(
        "professores/listar.html",
        professores=professores,
        busca=busca,
        tipo=session.get("tipo"),
        pode_editar=is_admin()
    )

@app.route("/professores/cadastrar")
def cadastrar_professor():
    if not is_admin():
        flash("Apenas administradores podem cadastrar professores.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("professores/cadastrar.html")

@app.route("/professores/salvar", methods=["POST"])
def salvar_professor():
    if not is_admin():
        flash("Apenas administradores podem cadastrar professores.", "danger")
        return redirect(url_for("dashboard"))
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
    return redirect(url_for("professores"))

@app.route("/professores/<int:prof_id>/editar")
def editar_professor(prof_id):
    if not is_admin():
        flash("Apenas administradores podem editar professores.", "danger")
        return redirect(url_for("dashboard"))
    professores = carregar_professores()
    prof = next((p for p in professores if p.id == prof_id), None)
    if not prof:
        flash("Professor não encontrado.", "danger")
        return redirect(url_for("professores"))
    return render_template("professores/editar.html", prof=prof)

@app.route("/professores/<int:prof_id>/atualizar", methods=["POST"])
def atualizar_professor(prof_id):
    if not is_admin():
        flash("Apenas administradores podem editar professores.", "danger")
        return redirect(url_for("dashboard"))
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
    return redirect(url_for("professores"))

@app.route("/professores/<int:prof_id>/excluir", methods=["POST"])
def excluir_professor(prof_id):
    if not is_admin():
        flash("Apenas administradores podem excluir professores.", "danger")
        return redirect(url_for("dashboard"))
    professores = carregar_professores()
    professores = [p for p in professores if p.id != prof_id]
    salvar_professores(professores)
    flash("Professor excluído com sucesso!", "success")
    return redirect(url_for("professores"))

# =========================
# BIBLIOTECA (COM CORREÇÃO DE DEVOLUÇÃO E PRINTS)
# =========================

# =========================
# BIBLIOTECA (COM ESTOQUE E LIMITE DE 1 LIVRO POR ALUNO)
# =========================

@app.route("/biblioteca")
def biblioteca():
    if requer_login():
        return redirect(url_for("login"))
    livros = carregar_json("livros.json")
    busca  = request.args.get("busca", "").lower()
    filtro = request.args.get("filtro", "todos")
    resultado = livros
    if busca:
        resultado = [l for l in resultado if busca in l["titulo"].lower() or busca in l.get("autor","").lower()]
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

    aluno_tem_livro = False
    if is_aluno():
        for livro in resultado:
            if livro.get("emprestado") and livro.get("emprestado_para") == session.get("usuario"):
                aluno_tem_livro = True
                break

    usuario_atual = session.get("usuario", "").strip().lower()
    email_atual = session.get("email", "").strip().lower()

    # Pega todos os alunos para buscar por email
    todos_alunos = carregar_alunos()

    for livro in resultado:
        emprestado_para = (livro.get("emprestado_para") or "").strip().lower()
        
        # Busca o aluno que está com o livro pelo nome
        aluno_do_livro = next((a for a in todos_alunos if a.nome and a.nome.strip().lower() == emprestado_para), None)
        email_do_aluno = aluno_do_livro.email.lower() if aluno_do_livro and aluno_do_livro.email else ""

        # PODE DEVOLVER SE:
        # 1. For staff
        # 2. For aluno E o email do aluno logado for igual ao email do aluno que pegou o livro
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

@app.route("/biblioteca/cadastrar")
def cadastrar_livro():
    if requer_login():
        return redirect(url_for("login"))
    if not is_admin():
        flash("Apenas administradores podem cadastrar livros.", "danger")
        return redirect(url_for("biblioteca"))
    return render_template("biblioteca/cadastrar.html")


@app.route("/biblioteca/salvar", methods=["POST"])
def salvar_livro():
    if requer_login():
        return redirect(url_for("login"))
    if not is_admin():
        flash("Apenas administradores podem cadastrar livros.", "danger")
        return redirect(url_for("biblioteca"))
    livros = carregar_json("livros.json")
    novo_id = max([l["id"] for l in livros], default=0) + 1
    
    # VALIDAÇÃO DO ANO (apenas números)
    ano = request.form.get("ano", "").strip()
    if not ano or not ano.isdigit():
        flash("Ano de publicação inválido. Use apenas números (ex: 2024).", "danger")
        return redirect(url_for("cadastrar_livro"))
    
    ano_int = int(ano)
    if ano_int < 1000 or ano_int > 9999:
        flash("Ano de publicação inválido. Use um ano entre 1000 e 9999.", "danger")
        return redirect(url_for("cadastrar_livro"))
    
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
        "id":         novo_id,
        "titulo":     request.form.get("titulo"),
        "autor":      request.form.get("autor"),
        "editora":    request.form.get("editora"),
        "ano":        str(ano_int),  # salva como string, mas já validado
        "genero":     request.form.get("genero"),
        "quantidade": quantidade,
        "estoque":    quantidade,
        "prazo_devolucao": prazo_devolucao,
        "emprestado": False,
        "emprestado_para": None,
        "data_emprestimo": None,
        "data_devolucao": None
    }
    livros.append(novo)
    salvar_json("livros.json", livros)
    flash(f"Livro cadastrado com sucesso! {quantidade} exemplar(es) em estoque. Prazo: {prazo_devolucao} dias.", "success")
    return redirect(url_for("biblioteca"))

@app.route("/biblioteca/<int:livro_id>/devolver", methods=["POST"])
def devolver_livro(livro_id):
    if requer_login():
        return redirect(url_for("login"))
    
    livros = carregar_json("livros.json")
    livro = next((l for l in livros if l["id"] == livro_id), None)
    if not livro:
        flash("Livro não encontrado.", "danger")
        return redirect(url_for("biblioteca"))
    
    if not livro.get("emprestado"):
        flash("Este livro não está emprestado.", "warning")
        return redirect(url_for("biblioteca"))
    
    email_atual = session.get("email", "").strip().lower()
    emprestado_para = (livro.get("emprestado_para") or "").strip().lower()
    
    # Busca o aluno pelo nome
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
        flash(f"Você não tem permissão para devolver este livro.", "danger")
    
    return redirect(url_for("biblioteca"))


@app.route("/biblioteca/<int:livro_id>/excluir", methods=["POST"])
def excluir_livro(livro_id):
    if requer_login():
        return redirect(url_for("login"))
    if not is_admin():
        flash("Apenas administradores podem excluir livros.", "danger")
        return redirect(url_for("biblioteca"))
    livros = carregar_json("livros.json")
    livros = [l for l in livros if l["id"] != livro_id]
    salvar_json("livros.json", livros)
    flash("Livro excluído com sucesso.", "success")
    return redirect(url_for("biblioteca"))

# =========================
# UPLOAD DE FOTO
# =========================

@app.route("/upload_foto", methods=["POST"])
def upload_foto():
    if requer_login():
        return redirect(url_for("login"))
    if not (is_aluno() or is_professor()):
        flash("Apenas alunos e professores podem enviar foto.", "danger")
        return redirect(url_for("dashboard"))
    
    if 'foto' not in request.files:
        flash("Nenhum arquivo selecionado.", "danger")
        return redirect(url_for("meu_perfil"))
    file = request.files['foto']
    if file.filename == '':
        flash("Nenhum arquivo selecionado.", "danger")
        return redirect(url_for("meu_perfil"))
    if not allowed_file(file.filename):
        flash("Formato inválido. Use apenas JPG ou PDF.", "danger")
        return redirect(url_for("meu_perfil"))
    
    email = session.get("email", "")
    if is_aluno():
        alunos = carregar_alunos()
        usuario = next((a for a in alunos if (a.email or "").lower() == email.lower()), None)
        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("meu_perfil"))
        filename = secure_filename(f"foto_aluno_{usuario.id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        usuario.foto = f"uploads/{filename}"
        salvar_alunos(alunos)
    elif is_professor():
        professores = carregar_professores()
        usuario = next((p for p in professores if (p.email or "").lower() == email.lower()), None)
        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("meu_perfil"))
        filename = secure_filename(f"foto_prof_{usuario.id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        usuario.foto = f"uploads/{filename}"
        salvar_professores(professores)
    
    flash("Foto atualizada com sucesso!", "success")
    return redirect(url_for("meu_perfil"))

# =========================
# NOTAS / BOLETIM
# =========================

@app.route("/notas/lancar", methods=["GET", "POST"])
def lancar_nota():
    if requer_login():
        return redirect(url_for("login"))
    if not is_professor():
        flash("Apenas professores podem lançar notas.", "danger")
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        aluno_id = request.form.get("aluno_id")
        disciplina = request.form.get("disciplina")
        bimestre = request.form.get("bimestre")
        nota = request.form.get("nota")
        
        if not all([aluno_id, disciplina, bimestre, nota]):
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for("lancar_nota"))
        
        try:
            bimestre = int(bimestre)
            if bimestre < 1 or bimestre > 4:
                flash("Bimestre deve ser entre 1 e 4.", "danger")
                return redirect(url_for("lancar_nota"))
            nota = float(nota)
            if nota < 0 or nota > 10:
                flash("Nota deve ser entre 0 e 10.", "danger")
                return redirect(url_for("lancar_nota"))
        except:
            flash("Valores inválidos.", "danger")
            return redirect(url_for("lancar_nota"))
        
        alunos = carregar_alunos()
        aluno = next((a for a in alunos if a.id == int(aluno_id)), None)
        if not aluno:
            flash("Aluno não encontrado.", "danger")
            return redirect(url_for("lancar_nota"))
        
        for n in aluno.notas:
            if n.get("disciplina", "").lower() == disciplina.lower() and n.get("bimestre") == bimestre:
                flash(f"Já existe nota para {disciplina} no {bimestre}º bimestre.", "warning")
                return redirect(url_for("lancar_nota"))
        
        aluno.adicionar_nota(disciplina, bimestre, nota)
        salvar_alunos(alunos)
        flash(f"Nota {nota} lançada para {aluno.nome} em {disciplina} ({bimestre}º bimestre).", "success")
        return redirect(url_for("lancar_nota"))
    
    alunos = carregar_alunos()
    disciplinas = ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês", "Artes", "Educação Física"]
    bimestres = [1, 2, 3, 4]
    return render_template("notas/lancar.html", alunos=alunos, disciplinas=disciplinas, bimestres=bimestres)

@app.route("/boletim/<int:aluno_id>")
def boletim(aluno_id):
    if requer_login():
        return redirect(url_for("login"))
    alunos = carregar_alunos()
    aluno = next((a for a in alunos if a.id == aluno_id), None)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for("dashboard"))
    
    # Permissões
    if is_aluno():
        email = session.get("email", "")
        aluno_logado = next((a for a in alunos if (a.email or "").lower() == email.lower()), None)
        if not aluno_logado or aluno_logado.id != aluno_id:
            flash("Você só pode ver seu próprio boletim.", "danger")
            return redirect(url_for("meu_perfil"))
    elif not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for("dashboard"))
    
    # Organiza notas
    disciplinas = sorted(set(n["disciplina"] for n in aluno.notas))
    dados_notas = {}
    for d in disciplinas:
        dados_notas[d] = {1: None, 2: None, 3: None, 4: None}
        for n in aluno.notas:
            if n["disciplina"] == d:
                bim = n.get("bimestre", 1)
                if 1 <= bim <= 4:
                    dados_notas[d][bim] = n["nota"]
    
    medias_disciplinas = {}
    for d in disciplinas:
        medias_disciplinas[d] = aluno.calcular_media_disciplina(d)
    
    media_geral = aluno.calcular_media_geral()
    situacao = None
    if media_geral is not None:
        situacao = "Aprovado" if media_geral >= 6 else "Reprovado"
    
    # Passa o tipo de usuário para o template
    return render_template(
        "notas/boletim.html",
        aluno=aluno,
        dados_notas=dados_notas,
        medias_disciplinas=medias_disciplinas,
        media_geral=media_geral,
        situacao=situacao,
        tipo_usuario=session.get("tipo")  # <-- ESSA LINHA É IMPORTANTE
    )

# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/biblioteca/emprestar", methods=["POST"])
def emprestar_livro_fixo():
    if requer_login():
        return redirect(url_for("login"))
    
    livro_id = request.form.get("livro_id")
    if not livro_id:
        flash("ID do livro não informado.", "danger")
        return redirect(url_for("biblioteca"))
    try:
        livro_id = int(livro_id)
    except:
        flash("ID inválido.", "danger")
        return redirect(url_for("biblioteca"))
    
    nome_aluno = request.form.get("nome_aluno", "").strip()
    if not nome_aluno:
        flash("Nome do aluno é obrigatório.", "danger")
        return redirect(url_for("biblioteca"))
    
    # Verifica se o aluno já tem um livro emprestado
    if is_aluno():
        email = session.get("email", "")
        alunos = carregar_alunos()
        aluno_logado = next((a for a in alunos if (a.email or "").lower() == email.lower()), None)
        if not aluno_logado:
            flash("Aluno não encontrado no sistema.", "danger")
            return redirect(url_for("biblioteca"))
        
        livros = carregar_json("livros.json")
        for l in livros:
            if l.get("emprestado_para") == nome_aluno and l.get("emprestado"):
                flash(f"O aluno {nome_aluno} já possui um livro emprestado.", "danger")
                return redirect(url_for("biblioteca"))
        
        nome_correto = aluno_logado.nome.strip().lower()
        nome_digitado = nome_aluno.strip().lower()
        if nome_digitado != nome_correto:
            flash(f"Aluno só pode emprestar livros para si mesmo.", "danger")
            return redirect(url_for("biblioteca"))
    
    livros = carregar_json("livros.json")
    livro_encontrado = None
    for l in livros:
        if l["id"] == livro_id:
            livro_encontrado = l
            break
    
    if not livro_encontrado:
        flash("Livro não encontrado.", "danger")
        return redirect(url_for("biblioteca"))
    
    if livro_encontrado.get("estoque", 0) <= 0:
        flash("Este livro não tem exemplares disponíveis.", "danger")
        return redirect(url_for("biblioteca"))
    
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
    return redirect(url_for("biblioteca"))

# =========================
# EXECUTAR
# =========================

if __name__ == "__main__":
    app.run(debug=True)