from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils import carregar_json, salvar_json
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# =========================
# DECORADOR PARA ROTAS PROTEGIDAS
# =========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Faça login para acessar esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# =========================
# HOME
# =========================
@auth_bp.route("/")
def home():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('dashboard.index'))

# =========================
# LOGIN
# =========================
@auth_bp.route("/login")
def login():
    erro = request.args.get("erro")
    return render_template("auth/login.html", erro=erro)

@auth_bp.route("/autenticar", methods=["POST"])
def autenticar():
    email = request.form.get("email")
    senha = request.form.get("senha")
    
    # Carrega usuários do JSON
    usuarios = carregar_json("usuarios.json")
    for usuario in usuarios:
        if usuario["email"] == email and usuario["senha"] == senha:
            session["usuario"] = usuario["nome"]
            session["tipo"] = usuario["tipo"]
            session["email"] = usuario["email"]
            return redirect(url_for('dashboard.index'))
    
    flash("Email ou senha inválidos.", "danger")
    return redirect(url_for('auth.login', erro=1))

# =========================
# CADASTRO DE USUÁRIO (público - todos viram aluno)
# =========================
@auth_bp.route("/cadastro")
def cadastro():
    return render_template("auth/cadastro.html", erro=0)

@auth_bp.route("/criar_conta", methods=["POST"])
def criar_conta():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    tipo = "aluno"
    
    # Carrega usuários do JSON
    usuarios = carregar_json("usuarios.json")
    for u in usuarios:
        if u["email"] == email:
            flash("Este email já está em uso.", "danger")
            return render_template("auth/cadastro.html", erro=1)
    
    # Cria usuário no JSON
    novo_usuario = {
        "nome": nome,
        "email": email,
        "senha": senha,
        "tipo": tipo
    }
    usuarios.append(novo_usuario)
    salvar_json("usuarios.json", usuarios)
    
    # Cria aluno automaticamente no JSON
    alunos = carregar_json("alunos.json")
    novo_id = max([a["id"] for a in alunos], default=0) + 1
    novo_aluno = {
        "id": novo_id,
        "nome": nome,
        "matricula": f"MAT{novo_id:04d}",
        "email": email,
        "data_nascimento": None,
        "serie": None,
        "turma": None,
        "telefone": None,
        "foto": None,
        "notas": [],
        "responsaveis": []
    }
    alunos.append(novo_aluno)
    salvar_json("alunos.json", alunos)
    
    flash("Conta criada com sucesso! Faça login.", "success")
    return redirect(url_for('auth.login'))

# =========================
# LOGOUT
# =========================
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('auth.login'))