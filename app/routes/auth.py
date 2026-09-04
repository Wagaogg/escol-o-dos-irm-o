from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.usuario import Usuario
from app.models.aluno import Aluno
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# =========================
# DECORADOR PARA ROTAS PROTEGIDAS
# =========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Faça login para acessar esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# =========================
# HOME
# =========================
@auth_bp.route("/")
def home():
    if 'usuario_id' not in session:
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
    
    # Busca usuário no SQLite
    usuario = Usuario.query.filter_by(email=email).first()
    
    if usuario and usuario.verificar_senha(senha):
        session.permanent = True
        session['usuario_id'] = usuario.id
        session['usuario'] = usuario.nome
        session['email'] = usuario.email
        session['tipo'] = usuario.tipo
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
    
    # Verifica se o email já existe
    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        flash("Este email já está em uso.", "danger")
        return render_template("auth/cadastro.html", erro=1)
    
    # Cria usuário no SQLite
    novo_usuario = Usuario(
        nome=nome,
        email=email,
        tipo=tipo
    )
    novo_usuario.senha_criptografada = senha  # criptografa a senha
    db.session.add(novo_usuario)
    db.session.flush()  # para pegar o ID
    
    # Cria aluno automaticamente no SQLite
    novo_aluno = Aluno(
        usuario_id=novo_usuario.id,
        matricula=f"MAT{novo_usuario.id:04d}",
        responsaveis="[]",
        notas="[]"
    )
    db.session.add(novo_aluno)
    db.session.commit()
    
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