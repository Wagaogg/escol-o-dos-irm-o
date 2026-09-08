from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.livro import Livro
from app.models.aluno import Aluno
from app.models.usuario import Usuario
from datetime import datetime, timedelta
import json

biblioteca_bp = Blueprint('biblioteca', __name__)

def is_admin():
    return session.get("tipo") in ["admin", "diretor"]

def is_staff():
    return session.get("tipo") in ["admin", "diretor", "professor"]

def is_aluno():
    return session.get("tipo") == "aluno"

def formatar_data_br(data):
    if not data:
        return "-"
    return data.strftime("%d/%m/%Y")

@biblioteca_bp.route("/biblioteca")
def listar():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    livros = Livro.query.all()
    busca = request.args.get("busca", "").lower()
    filtro = request.args.get("filtro", "todos")
    
    resultado = livros
    if busca:
        resultado = [l for l in resultado if busca in l.titulo.lower() or busca in (l.autor or "").lower()]
    
    if filtro == "disponivel":
        resultado = [l for l in resultado if l.estoque > 0]
    elif filtro == "emprestado":
        resultado = [l for l in resultado if l.estoque == 0]
    
    nome_aluno_logado = None
    if is_aluno():
        usuario_id = session.get('usuario_id')
        aluno = Aluno.query.filter_by(usuario_id=usuario_id).first()
        if aluno and aluno.usuario:
            nome_aluno_logado = aluno.usuario.nome
    
    # Verifica se o ALUNO LOGADO já tem um livro emprestado (usando nome normalizado)
    aluno_tem_livro = False
    if is_aluno():
        usuario_id = session.get('usuario_id')
        aluno = Aluno.query.filter_by(usuario_id=usuario_id).first()
        if aluno and aluno.usuario:
            nome_aluno = aluno.usuario.nome.strip().lower()
            livro_emprestado = Livro.query.filter(
                Livro.emprestado_para.isnot(None),
                db.func.lower(Livro.emprestado_para) == nome_aluno
            ).first()
            if livro_emprestado:
                aluno_tem_livro = True
    
    livros_lista = []
    for livro in resultado:
        esta_emprestado = livro.emprestado_para is not None
        
        # 🔥 LÓGICA DE PODE_DEVOLVER (com logs)
        pode_devolver = False
        if esta_emprestado:
            if is_staff():
                pode_devolver = True
                print(f"✅ STAFF: pode devolver {livro.titulo}")
            elif is_aluno():
                usuario_id = session.get('usuario_id')
                aluno = Aluno.query.filter_by(usuario_id=usuario_id).first()
                if aluno and aluno.usuario:
                    nome_aluno = aluno.usuario.nome.strip().lower()
                    nome_emprestado = livro.emprestado_para.strip().lower()
                    # 🔥 LOG PARA DEBUG
                    print(f"🔍 Aluno logado: '{nome_aluno}' | Emprestado para: '{nome_emprestado}' | Livro: {livro.titulo}")
                    if nome_aluno == nome_emprestado:
                        pode_devolver = True
                        print(f"✅ PODE DEVOLVER: {nome_aluno} == {nome_emprestado}")
                    else:
                        pode_devolver = False
                        print(f"❌ NÃO PODE DEVOLVER: {nome_aluno} != {nome_emprestado}")
        
        # Pode emprestar se: estoque > 0 e (staff ou (aluno sem livro))
        pode_emprestar = False
        if livro.estoque > 0:
            if is_staff():
                pode_emprestar = True
            elif is_aluno() and not aluno_tem_livro:
                pode_emprestar = True
        
        livros_lista.append({
            "id": livro.id,
            "titulo": livro.titulo,
            "autor": livro.autor,
            "editora": livro.editora,
            "ano": livro.ano,
            "genero": livro.genero,
            "quantidade": livro.quantidade,
            "estoque": livro.estoque,
            "estoque_display": livro.estoque,
            "emprestado": esta_emprestado,
            "data_devolucao_br": formatar_data_br(livro.data_devolucao),
            "pode_devolver": pode_devolver,
            "pode_emprestar": pode_emprestar
        })
    
    return render_template(
        "biblioteca/listar.html",
        livros=livros_lista,
        busca=busca,
        filtro=filtro,
        tipo=session.get("tipo"),
        nome_aluno_logado=nome_aluno_logado
    )

@biblioteca_bp.route("/biblioteca/cadastrar")
def cadastrar_livro():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar livros.", "danger")
        return redirect(url_for('biblioteca.listar'))
    return render_template("biblioteca/cadastrar.html")

@biblioteca_bp.route("/biblioteca/salvar", methods=["POST"])
def salvar_livro():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem cadastrar livros.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    titulo = request.form.get("titulo")
    autor = request.form.get("autor")
    editora = request.form.get("editora")
    ano = request.form.get("ano")
    genero = request.form.get("genero")
    
    if ano and not ano.isdigit():
        flash("Ano de publicação inválido. Use apenas números.", "danger")
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
    
    novo_livro = Livro(
        titulo=titulo,
        autor=autor,
        editora=editora,
        ano=ano,
        genero=genero,
        quantidade=quantidade,
        estoque=quantidade,
        prazo_devolucao=prazo_devolucao,
        emprestado_para=None,
        data_emprestimo=None,
        data_devolucao=None
    )
    db.session.add(novo_livro)
    db.session.commit()
    
    flash(f"Livro cadastrado com sucesso! {quantidade} exemplar(es) em estoque. Prazo: {prazo_devolucao} dias.", "success")
    return redirect(url_for('biblioteca.listar'))

@biblioteca_bp.route("/biblioteca/emprestar", methods=["POST"])
def emprestar_livro():
    if 'usuario_id' not in session:
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
    
    livro = Livro.query.get(livro_id)
    if not livro:
        flash("Livro não encontrado.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    if livro.estoque <= 0:
        flash("Este livro não tem exemplares disponíveis.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    if is_aluno():
        usuario_id = session.get('usuario_id')
        aluno = Aluno.query.filter_by(usuario_id=usuario_id).first()
        if not aluno:
            flash("Aluno não encontrado no sistema.", "danger")
            return redirect(url_for('biblioteca.listar'))
        
        nome_aluno_logado = aluno.usuario.nome.strip().lower()
        # Verifica se o aluno já tem um livro emprestado
        livro_emprestado = Livro.query.filter(
            Livro.emprestado_para.isnot(None),
            db.func.lower(Livro.emprestado_para) == nome_aluno_logado
        ).first()
        if livro_emprestado:
            flash(f"Você já possui um livro emprestado: {livro_emprestado.titulo}. Devolva antes de pegar outro.", "danger")
            return redirect(url_for('biblioteca.listar'))
        
        # Verifica se o nome digitado é o próprio aluno
        if nome_aluno.lower() != nome_aluno_logado:
            flash("Aluno só pode emprestar livros para si mesmo.", "danger")
            return redirect(url_for('biblioteca.listar'))
    
    # Realiza empréstimo
    livro.estoque -= 1
    livro.emprestado_para = nome_aluno
    livro.data_emprestimo = datetime.now().date()
    prazo_dias = livro.prazo_devolucao or 7
    livro.data_devolucao = datetime.now().date() + timedelta(days=prazo_dias)
    
    db.session.commit()
    
    data_br = livro.data_devolucao.strftime("%d/%m/%Y")
    flash(f"Empréstimo realizado! {livro.titulo} - Devolver até: {data_br}.", "success")
    return redirect(url_for('biblioteca.listar'))

@biblioteca_bp.route("/biblioteca/<int:livro_id>/devolver", methods=["POST"])
def devolver_livro(livro_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    livro = Livro.query.get(livro_id)
    if not livro:
        flash("Livro não encontrado.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    if not livro.emprestado_para:
        flash("Este livro não está emprestado.", "warning")
        return redirect(url_for('biblioteca.listar'))
    
    # 🔥 LÓGICA DE DEVOLUÇÃO (com logs)
    pode_devolver = False
    if is_staff():
        pode_devolver = True
        print(f"✅ STAFF: devolvendo {livro.titulo}")
    elif is_aluno():
        usuario_id = session.get('usuario_id')
        aluno = Aluno.query.filter_by(usuario_id=usuario_id).first()
        if aluno and aluno.usuario:
            nome_aluno = aluno.usuario.nome.strip().lower()
            nome_emprestado = livro.emprestado_para.strip().lower()
            print(f"🔍 Aluno logado: '{nome_aluno}' | Emprestado para: '{nome_emprestado}' | Livro: {livro.titulo}")
            if nome_aluno == nome_emprestado:
                pode_devolver = True
                print(f"✅ PODE DEVOLVER: {nome_aluno} == {nome_emprestado}")
            else:
                pode_devolver = False
                print(f"❌ NÃO PODE DEVOLVER: {nome_aluno} != {nome_emprestado}")
    
    if pode_devolver:
        livro.estoque += 1
        livro.emprestado_para = None
        livro.data_emprestimo = None
        livro.data_devolucao = None
        db.session.commit()
        flash(f"Livro devolvido com sucesso! Estoque atual: {livro.estoque} exemplar(es).", "success")
    else:
        flash("Você não tem permissão para devolver este livro.", "danger")
    
    return redirect(url_for('biblioteca.listar'))

@biblioteca_bp.route("/biblioteca/<int:livro_id>/excluir", methods=["POST"])
def excluir_livro(livro_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_admin():
        flash("Apenas administradores podem excluir livros.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    livro = Livro.query.get(livro_id)
    if not livro:
        flash("Livro não encontrado.", "danger")
        return redirect(url_for('biblioteca.listar'))
    
    db.session.delete(livro)
    db.session.commit()
    flash("Livro excluído com sucesso.", "success")
    return redirect(url_for('biblioteca.listar'))