from flask import Blueprint, render_template, session, flash, redirect, url_for, request, current_app
from app import db
from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.livro import Livro
from werkzeug.utils import secure_filename
import os
import json

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
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    usuario_id = session.get('usuario_id')
    
    if is_aluno():
        aluno = Aluno.query.filter_by(usuario_id=usuario_id).first()
        if not aluno:
            flash("Perfil de aluno não encontrado.", "danger")
            return redirect(url_for('dashboard.index'))
        
        # Carrega dados do JSON (responsaveis e notas)
        responsaveis = json.loads(aluno.responsaveis) if aluno.responsaveis else []
        notas = json.loads(aluno.notas) if aluno.notas else []
        
        # Livros emprestados (SQLite)
        livros_emprestados = Livro.query.filter_by(emprestado=True, emprestado_para=session.get('usuario')).all()
        
        return render_template("alunos/meu_perfil.html", 
            usuario=session["usuario"], 
            tipo=session["tipo"], 
            aluno={
                "id": aluno.id,
                "nome": session.get("usuario"),
                "email": session.get("email"),
                "matricula": aluno.matricula,
                "turma": aluno.turma,
                "serie": aluno.serie,
                "data_nascimento": aluno.data_nascimento.strftime("%d/%m/%Y") if aluno.data_nascimento else None,
                "telefone": aluno.telefone,
                "foto": Usuario.query.get(usuario_id).foto,
                "responsaveis": responsaveis,
                "notas": notas
            }, 
            livros_emprestados=livros_emprestados, 
            foto=Usuario.query.get(usuario_id).foto
        )
    
    elif is_professor():
        professor = Professor.query.filter_by(usuario_id=usuario_id).first()
        if not professor:
            flash("Perfil de professor não encontrado.", "danger")
            return redirect(url_for('dashboard.index'))
        
        return render_template("professores/meu_perfil.html", 
            usuario=session["usuario"], 
            tipo=session["tipo"], 
            professor={
                "id": professor.id,
                "nome": session.get("usuario"),
                "email": session.get("email"),
                "materia": professor.materia,
                "turmas": professor.turmas,
                "telefone": Usuario.query.get(usuario_id).telefone,
                "foto": Usuario.query.get(usuario_id).foto
            }, 
            foto=Usuario.query.get(usuario_id).foto
        )
    else:
        return redirect(url_for('dashboard.index'))

# =========================
# UPLOAD DE FOTO
# =========================
@meu_perfil_bp.route("/upload_foto", methods=["POST"])
def upload_foto():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    usuario_id = session.get('usuario_id')
    usuario = Usuario.query.get(usuario_id)
    
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for('meu_perfil.meu_perfil'))
    
    if 'foto' not in request.files:
        flash("Nenhum arquivo selecionado.", "danger")
        return redirect(url_for('meu_perfil.meu_perfil'))
    
    file = request.files['foto']
    if file.filename == '':
        flash("Nenhum arquivo selecionado.", "danger")
        return redirect(url_for('meu_perfil.meu_perfil'))
    
    # Validação de extensão
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'pdf'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        flash("Formato inválido. Use JPG, PNG, GIF ou PDF.", "danger")
        return redirect(url_for('meu_perfil.meu_perfil'))
    
    # Salva o arquivo
    filename = secure_filename(f"foto_{usuario_id}_{file.filename}")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Atualiza o campo foto no SQLite
    usuario.foto = f"uploads/{filename}"
    db.session.commit()
    
    flash("Foto atualizada com sucesso!", "success")
    return redirect(url_for('meu_perfil.meu_perfil'))