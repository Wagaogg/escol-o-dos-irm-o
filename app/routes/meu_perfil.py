from flask import Blueprint, render_template, session, flash, redirect, url_for, request, current_app
from app.utils import carregar_alunos, carregar_professores, carregar_json, salvar_json, salvar_alunos, salvar_professores, allowed_file
from app.models.aluno import Aluno
from app.models.professor import Professor
from werkzeug.utils import secure_filename
import os

meu_perfil_bp = Blueprint('meu_perfil', __name__)

# =========================
# PERMISSÕES
# =========================
def is_aluno():
    return session.get("tipo") == "aluno"

def is_professor():
    return session.get("tipo") == "professor"

# =========================
# MEU PERFIL
# =========================
@meu_perfil_bp.route("/meu_perfil")
def meu_perfil():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
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
        return render_template("alunos/meu_perfil.html", 
            usuario=session["usuario"], 
            tipo=session["tipo"], 
            aluno=aluno, 
            livros_emprestados=livros_emprestados, 
            foto=aluno.foto
        )
    
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
        return render_template("professores/meu_perfil.html", 
            usuario=session["usuario"], 
            tipo=session["tipo"], 
            professor=professor, 
            foto=professor.foto
        )
    else:
        return redirect(url_for('dashboard.home'))

# =========================
# UPLOAD DE FOTO
# =========================
@meu_perfil_bp.route("/upload_foto", methods=["POST"])
def upload_foto():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not (is_aluno() or is_professor()):
        flash("Apenas alunos e professores podem enviar foto.", "danger")
        return redirect(url_for('dashboard.home'))
    
    if 'foto' not in request.files:
        flash("Nenhum arquivo selecionado.", "danger")
        return redirect(url_for('meu_perfil.meu_perfil'))
    
    file = request.files['foto']
    if file.filename == '':
        flash("Nenhum arquivo selecionado.", "danger")
        return redirect(url_for('meu_perfil.meu_perfil'))
    
    if not allowed_file(file.filename):
        flash("Formato inválido. Use apenas JPG ou PDF.", "danger")
        return redirect(url_for('meu_perfil.meu_perfil'))
    
    email = session.get("email", "")
    if is_aluno():
        alunos = carregar_alunos()
        usuario = next((a for a in alunos if (a.email or "").lower() == email.lower()), None)
        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for('meu_perfil.meu_perfil'))
        filename = secure_filename(f"foto_aluno_{usuario.id}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        usuario.foto = f"uploads/{filename}"
        salvar_alunos(alunos)
    
    elif is_professor():
        professores = carregar_professores()
        usuario = next((p for p in professores if (p.email or "").lower() == email.lower()), None)
        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for('meu_perfil.meu_perfil'))
        filename = secure_filename(f"foto_prof_{usuario.id}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        usuario.foto = f"uploads/{filename}"
        salvar_professores(professores)
    
    flash("Foto atualizada com sucesso!", "success")
    return redirect(url_for('meu_perfil.meu_perfil'))