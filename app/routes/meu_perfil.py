from flask import Blueprint, render_template, session, flash, redirect, url_for, request, current_app
from app import db
from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.livro import Livro
from app.models.conquista import Conquista
from app.utils_conquistas import get_conquistas_por_publico, RARIDADES
from werkzeug.utils import secure_filename
import os
import json

meu_perfil_bp = Blueprint('meu_perfil', __name__)

def is_aluno():
    return session.get("tipo") == "aluno"

def is_professor():
    return session.get("tipo") == "professor"


@meu_perfil_bp.route("/meu_perfil")
def meu_perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    usuario_id = session.get('usuario_id')
    usuario = Usuario.query.get(usuario_id)

    if is_aluno():
        aluno = Aluno.query.filter_by(usuario_id=usuario_id).first()
        if not aluno:
            flash("Perfil de aluno não encontrado.", "danger")
            return redirect(url_for('dashboard.index'))

        responsaveis = json.loads(aluno.responsaveis) if aluno.responsaveis else []
        livros_emprestados = Livro.query.filter_by(emprestado=True, emprestado_para=usuario.nome).all()

        # 🔥 Só conquistas de aluno
        conquistas_publico = get_conquistas_por_publico("aluno")

        conquistas_db = Conquista.query.filter_by(usuario_id=usuario_id).all()
        codigos_desbloqueados = {c.codigo: c.desbloqueada_em for c in conquistas_db}

        conquistas_lista = []
        for codigo, info in conquistas_publico.items():
            if codigo in codigos_desbloqueados:
                conquistas_lista.append({
                    "codigo": codigo,
                    "nome": info["nome"],
                    "descricao": info["descricao"],
                    "detalhamento": info.get("detalhamento", ""),
                    "icone": info["icone"],
                    "categoria": info["categoria"],
                    "raridade": info.get("raridade", "comum"),
                    "raridade_info": RARIDADES.get(info.get("raridade", "comum"), RARIDADES["comum"]),
                    "desbloqueada": True,
                    "data": codigos_desbloqueados[codigo],
                })

        conquistas_lista = sorted(conquistas_lista, key=lambda x: x["data"], reverse=True)

        total_conquistas = len(conquistas_publico)
        total_desbloqueadas = len(conquistas_lista)
        percentual = round((total_desbloqueadas / total_conquistas) * 100) if total_conquistas > 0 else 0

        return render_template(
            "alunos/meu_perfil.html",
            usuario=usuario,
            aluno=aluno,
            foto=usuario.foto,
            responsaveis=responsaveis,
            livros_emprestados=livros_emprestados,
            conquistas=conquistas_lista,
            total_conquistas=total_conquistas,
            total_desbloqueadas=total_desbloqueadas,
            percentual_conquistas=percentual,
        )

    elif is_professor():
        professor = Professor.query.filter_by(usuario_id=usuario_id).first()
        if not professor:
            flash("Perfil de professor não encontrado.", "danger")
            return redirect(url_for('dashboard.index'))

        # 🔥 Conquistas de professor (opcional exibir no perfil do professor)
        conquistas_publico = get_conquistas_por_publico("professor")
        conquistas_db = Conquista.query.filter_by(usuario_id=usuario_id).all()
        codigos_desbloqueados = {c.codigo: c.desbloqueada_em for c in conquistas_db}

        conquistas_lista = []
        for codigo, info in conquistas_publico.items():
            if codigo in codigos_desbloqueados:
                conquistas_lista.append({
                    "codigo": codigo,
                    "nome": info["nome"],
                    "descricao": info["descricao"],
                    "detalhamento": info.get("detalhamento", ""),
                    "icone": info["icone"],
                    "categoria": info["categoria"],
                    "raridade": info.get("raridade", "comum"),
                    "raridade_info": RARIDADES.get(info.get("raridade", "comum"), RARIDADES["comum"]),
                    "desbloqueada": True,
                    "data": codigos_desbloqueados[codigo],
                })
        conquistas_lista = sorted(conquistas_lista, key=lambda x: x["data"], reverse=True)

        total_conquistas = len(conquistas_publico)
        total_desbloqueadas = len(conquistas_lista)
        percentual = round((total_desbloqueadas / total_conquistas) * 100) if total_conquistas > 0 else 0

        return render_template(
            "professores/meu_perfil.html",
            usuario=usuario,
            professor=professor,
            foto=usuario.foto,
            conquistas=conquistas_lista,
            total_conquistas=total_conquistas,
            total_desbloqueadas=total_desbloqueadas,
            percentual_conquistas=percentual,
        )
    else:
        return redirect(url_for('dashboard.index'))


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

    allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        flash("Formato inválido. Use JPG, PNG ou PDF.", "danger")
        return redirect(url_for('meu_perfil.meu_perfil'))

    filename = secure_filename(f"foto_{usuario_id}_{file.filename}")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    usuario.foto = f"uploads/{filename}"
    db.session.commit()

    flash("Foto atualizada com sucesso!", "success")
    return redirect(url_for('meu_perfil.meu_perfil'))