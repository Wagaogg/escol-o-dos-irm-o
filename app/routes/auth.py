from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.models.professor import Professor
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
    
    usuario = Usuario.query.filter_by(email=email).first()
    
    if usuario and usuario.verificar_senha(senha):
        # 🔥 Verifica se é professor
        prof = Professor.query.filter_by(usuario_id=usuario.id).first()
        
        if prof:
            if usuario.tipo != "professor":
                usuario.tipo = "professor"
                db.session.commit()
            session['tipo'] = "professor"
        else:
            session['tipo'] = usuario.tipo
        
        session.permanent = True
        session['usuario_id'] = usuario.id
        session['usuario'] = usuario.nome
        session['email'] = usuario.email
        
        return redirect(url_for('dashboard.index'))
    
    flash("Email ou senha inválidos.", "danger")
    return redirect(url_for('auth.login', erro=1))

# =========================
# CADASTRO DE USUÁRIO
# =========================
@auth_bp.route("/cadastro")
def cadastro():
    return render_template("auth/cadastro.html", erro=0)

@auth_bp.route("/criar_conta", methods=["POST"])
def criar_conta():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    
    # Verifica se o email já está em uso
    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        flash("Este email já está em uso.", "danger")
        return render_template("auth/cadastro.html", erro=1)
    
    # 🔥 VERIFICA SE O EMAIL JÁ ESTÁ CADASTRADO COMO PROFESSOR
    professor_existente = Professor.query.filter(
        db.func.lower(Professor.email) == email.lower()
    ).first()
    
    if professor_existente:
        # Já é professor cadastrado → cria como professor
        novo_usuario = Usuario(nome=nome, email=email, tipo="professor")
        novo_usuario.senha_criptografada = senha
        db.session.add(novo_usuario)
        db.session.flush()
        
        # Vincula o professor ao usuário
        professor_existente.usuario_id = novo_usuario.id
        db.session.commit()
        
        flash("Conta de professor criada com sucesso! Faça login.", "success")
        return redirect(url_for('auth.login'))
    
    # Se não for professor, cria como aluno
    novo_usuario = Usuario(nome=nome, email=email, tipo="aluno")
    novo_usuario.senha_criptografada = senha
    db.session.add(novo_usuario)
    db.session.flush()
    
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