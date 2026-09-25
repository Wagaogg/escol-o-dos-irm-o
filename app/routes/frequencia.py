from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db
from app.models.frequencia import Frequencia
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.usuario import Usuario
from app.models.notificacao import Notificacao
from datetime import datetime
import json
import re

frequencia_bp = Blueprint('frequencia', __name__)

def is_admin():
    return session.get("tipo") in ["admin", "diretor"]

def is_staff():
    return session.get("tipo") in ["admin", "diretor", "professor"]

def is_professor():
    return session.get("tipo") == "professor"

def is_aluno():
    return session.get("tipo") == "aluno"

def normalizar(texto):
    if not texto:
        return ""
    texto = str(texto).lower()
    texto = re.sub(r'[^a-z0-9]', '', texto)
    return texto

# =========================
# ESCOLHER TURMA
# =========================
@frequencia_bp.route("/frequencia/chamada", methods=["GET"])
def chamada():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    turmas_dict = {}
    for a in Aluno.query.all():
        if a.turma:
            norm = normalizar(a.turma)
            if norm and norm not in turmas_dict:
                turmas_dict[norm] = a.turma.strip()
    
    turmas = sorted(turmas_dict.values())
    disciplinas = ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês", "Artes", "Educação Física"]
    
    return render_template("frequencia/chamada.html", turmas=turmas, disciplinas=disciplinas)

# =========================
# MARCAR LISTA
# =========================
@frequencia_bp.route("/frequencia/marcar_lista", methods=["POST"])
def marcar_lista():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    turma = request.form.get("turma")
    disciplina = request.form.get("disciplina")
    data_str = request.form.get("data")
    
    if not all([turma, disciplina, data_str]):
        flash("Preencha todos os campos.", "danger")
        return redirect(url_for('frequencia.chamada'))
    
    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    except:
        flash("Data inválida.", "danger")
        return redirect(url_for('frequencia.chamada'))
    
    turma_norm = normalizar(turma)
    alunos = [a for a in Aluno.query.all() if a.turma and normalizar(a.turma) == turma_norm]
    
    registros_existentes = {}
    for f in Frequencia.query.filter_by(disciplina=disciplina, data=data_obj).all():
        registros_existentes[f.aluno_id] = f
    
    alunos_info = []
    for a in alunos:
        existing = registros_existentes.get(a.id)
        alunos_info.append({
            "id": a.id,
            "nome": a.usuario.nome if a.usuario else "Sem nome",
            "matricula": a.matricula,
            "foto": a.usuario.foto if a.usuario else None,
            "status_atual": existing.status if existing else "presente",
            "observacao_atual": existing.observacao if existing else ""
        })
    
    total_presentes = sum(1 for a in alunos_info if a["status_atual"] == "presente")
    total_faltas = sum(1 for a in alunos_info if a["status_atual"] == "falta")
    total_justificadas = sum(1 for a in alunos_info if a["status_atual"] == "justificada")
    
    return render_template(
        "frequencia/marcar_lista.html",
        turma=turma,
        disciplina=disciplina,
        data=data_str,
        data_br=data_obj.strftime("%d/%m/%Y"),
        alunos=alunos_info,
        total_alunos=len(alunos_info),
        total_presentes=total_presentes,
        total_faltas=total_faltas,
        total_justificadas=total_justificadas
    )

# =========================
# SALVAR CHAMADA
# =========================
@frequencia_bp.route("/frequencia/salvar", methods=["POST"])
def salvar():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    turma = request.form.get("turma")
    disciplina = request.form.get("disciplina")
    data_str = request.form.get("data")
    
    if not all([turma, disciplina, data_str]):
        flash("Parâmetros inválidos.", "danger")
        return redirect(url_for('frequencia.chamada'))
    
    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    except:
        flash("Data inválida.", "danger")
        return redirect(url_for('frequencia.chamada'))
    
    professor_id = None
    if is_professor():
        usuario_id = session.get('usuario_id')
        prof = Professor.query.filter_by(usuario_id=usuario_id).first()
        if prof:
            professor_id = prof.id
    
    turma_norm = normalizar(turma)
    alunos = [a for a in Aluno.query.all() if a.turma and normalizar(a.turma) == turma_norm]
    
    total_salvos = 0
    for aluno in alunos:
        status = request.form.get(f"status_{aluno.id}", "presente")
        observacao = request.form.get(f"obs_{aluno.id}", "").strip()
        
        existente = Frequencia.query.filter_by(
            aluno_id=aluno.id,
            disciplina=disciplina,
            data=data_obj
        ).first()
        
        if existente:
            existente.status = status
            existente.observacao = observacao
            existente.professor_id = professor_id
        else:
            nova = Frequencia(
                aluno_id=aluno.id,
                professor_id=professor_id,
                disciplina=disciplina,
                data=data_obj,
                status=status,
                observacao=observacao
            )
            db.session.add(nova)
        
        if status == "falta":
            notif = Notificacao(
                usuario_id=aluno.usuario_id,
                mensagem=f"Falta registrada em {disciplina} no dia {data_obj.strftime('%d/%m/%Y')}.",
                link=url_for('frequencia.minha_frequencia')
            )
            db.session.add(notif)
        
        total_salvos += 1
    
    db.session.commit()
    
    # 🔥 VERIFICAR CONQUISTAS DE CADA ALUNO
    from app.routes.conquistas import verificar_conquistas
    for aluno in alunos:
        verificar_conquistas(aluno.usuario_id)
    
    flash(f"Chamada salva! {total_salvos} aluno(s) registrado(s).", "success")
    return redirect(url_for('frequencia.relatorio'))

# =========================
# MINHA FREQUÊNCIA (ALUNO)
# =========================
@frequencia_bp.route("/frequencia/minha")
def minha_frequencia():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_aluno():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    usuario_id = session.get('usuario_id')
    aluno = Aluno.query.filter_by(usuario_id=usuario_id).first()
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    frequencias = Frequencia.query.filter_by(aluno_id=aluno.id).order_by(Frequencia.data.desc()).all()
    
    disciplinas = {}
    for f in frequencias:
        if f.disciplina not in disciplinas:
            disciplinas[f.disciplina] = {"presente": 0, "falta": 0, "justificada": 0}
        disciplinas[f.disciplina][f.status] += 1
    
    for d, stats in disciplinas.items():
        total = stats["presente"] + stats["falta"] + stats["justificada"]
        stats["total"] = total
        stats["percentual"] = round((stats["presente"] / total) * 100, 1) if total > 0 else 0
    
    return render_template(
        "frequencia/minha_frequencia.html",
        aluno=aluno,
        frequencias=frequencias,
        disciplinas=disciplinas
    )

# =========================
# RELATÓRIO
# =========================
@frequencia_bp.route("/frequencia/relatorio")
def relatorio():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    turma = request.args.get("turma", "")
    disciplina = request.args.get("disciplina", "")
    
    frequencias = Frequencia.query.order_by(Frequencia.data.desc()).all()
    
    if disciplina:
        frequencias = [f for f in frequencias if f.disciplina == disciplina]
    
    if turma:
        turma_norm = normalizar(turma)
        frequencias = [
            f for f in frequencias
            if f.aluno and f.aluno.turma and normalizar(f.aluno.turma) == turma_norm
        ]
    
    alunos_stats = {}
    for f in frequencias:
        aluno = f.aluno
        if not aluno:
            continue
        key = aluno.id
        if key not in alunos_stats:
            alunos_stats[key] = {
                "id": aluno.id,
                "nome": aluno.usuario.nome if aluno.usuario else "Sem nome",
                "matricula": aluno.matricula,
                "turma": aluno.turma,
                "presente": 0,
                "falta": 0,
                "justificada": 0
            }
        if f.status == "presente":
            alunos_stats[key]["presente"] += 1
        elif f.status == "falta":
            alunos_stats[key]["falta"] += 1
        elif f.status == "justificada":
            alunos_stats[key]["justificada"] += 1
    
    for key, stats in alunos_stats.items():
        total = stats["presente"] + stats["falta"] + stats["justificada"]
        stats["total"] = total
        stats["percentual"] = round((stats["presente"] / total) * 100, 1) if total > 0 else 0
    
    turmas = sorted(set(a.turma for a in Aluno.query.all() if a.turma))
    disciplinas = ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês", "Artes", "Educação Física"]
    
    return render_template(
        "frequencia/relatorio.html",
        alunos_stats=list(alunos_stats.values()),
        turmas=turmas,
        disciplinas=disciplinas,
        turma_filtro=turma,
        disciplina_filtro=disciplina
    )