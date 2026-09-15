from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db
from app.models.frequencia import Frequencia
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.usuario import Usuario
from app.models.notificacao import Notificacao
from datetime import datetime, date
import json

frequencia_bp = Blueprint('frequencia', __name__)

def is_admin():
    return session.get("tipo") in ["admin", "diretor"]

def is_staff():
    return session.get("tipo") in ["admin", "diretor", "professor"]

def is_professor():
    return session.get("tipo") == "professor"

def is_aluno():
    return session.get("tipo") == "aluno"

# =========================
# FAZER CHAMADA (ESCOLHER TURMA/DISCIPLINA/DATA)
# =========================
@frequencia_bp.route("/frequencia/chamada", methods=["GET"])
def chamada():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    turmas = set()
    if is_professor():
        usuario_id = session.get('usuario_id')
        prof = Professor.query.filter_by(usuario_id=usuario_id).first()
        if prof and prof.turmas_lista:
            try:
                turmas = set(json.loads(prof.turmas_lista))
            except:
                turmas = set()
        if not turmas:
            turmas = set(a.turma for a in Aluno.query.all() if a.turma)
    else:
        turmas = set(a.turma for a in Aluno.query.all() if a.turma)
    
    turmas = sorted([t for t in turmas if t])
    disciplinas = ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês", "Artes", "Educação Física"]
    
    return render_template("frequencia/chamada.html", turmas=turmas, disciplinas=disciplinas)

# =========================
# MARCAR LISTA (TODOS DE UMA VEZ) - POST
# =========================
@frequencia_bp.route("/frequencia/marcar_lista", methods=["GET", "POST"])
def marcar_lista():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    # GET e POST
    if request.method == "POST":
        turma = request.form.get("turma")
        disciplina = request.form.get("disciplina")
        data_str = request.form.get("data")
    else:
        turma = request.args.get("turma")
        disciplina = request.args.get("disciplina")
        data_str = request.args.get("data")
    
    if not all([turma, disciplina, data_str]):
        flash("Parâmetros inválidos.", "danger")
        return redirect(url_for('frequencia.chamada'))
    
    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    except:
        flash("Data inválida.", "danger")
        return redirect(url_for('frequencia.chamada'))
    
    # 🔥 Busca alunos da turma (comparação em Python, case-insensitive e sem espaços)
    turma_normalizada = turma.strip().lower()
    alunos = [
        a for a in Aluno.query.all()
        if a.turma and a.turma.strip().lower() == turma_normalizada
    ]
    
    # Busca registros existentes
    registros_existentes = {}
    for f in Frequencia.query.filter_by(disciplina=disciplina, data=data_obj).all():
        registros_existentes[f.aluno_id] = f
    
    # Se for POST, salva
    if request.method == "POST":
        aluno_ids = request.form.getlist("aluno_ids")
        statuses = request.form.getlist("status[]")
        observacoes = request.form.getlist("observacao[]")
        
        for i, aluno_id in enumerate(aluno_ids):
            aluno = Aluno.query.get(int(aluno_id))
            if not aluno:
                continue
            
            status = statuses[i] if i < len(statuses) else "presente"
            observacao = observacoes[i] if i < len(observacoes) else ""
            
            existente = Frequencia.query.filter_by(
                aluno_id=aluno.id,
                disciplina=disciplina,
                data=data_obj
            ).first()
            
            if existente:
                existente.status = status
                existente.observacao = observacao
            else:
                nova = Frequencia(
                    aluno_id=aluno.id,
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
        
        db.session.commit()
        flash(f"Frequência registrada para a turma {turma}!", "success")
        return redirect(url_for('frequencia.relatorio', turma=turma))
    
    # GET - mostra a lista
    alunos_info = []
    for a in alunos:
        existing = registros_existentes.get(a.id)
        alunos_info.append({
            "id": a.id,
            "nome": a.usuario.nome if a.usuario else "Sem nome",
            "matricula": a.matricula,
            "status_atual": existing.status if existing else "presente",
            "observacao_atual": existing.observacao if existing else ""
        })
    
    return render_template(
        "frequencia/marcar_lista.html",
        turma=turma,
        disciplina=disciplina,
        data=data_str,
        data_br=data_obj.strftime("%d/%m/%Y"),
        alunos=alunos_info
    )

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
# RELATÓRIO POR TURMA
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
    
    query = Frequencia.query
    if disciplina:
        query = query.filter_by(disciplina=disciplina)
    
    frequencias = query.order_by(Frequencia.data.desc()).all()
    
    if turma:
        turma_normalizada = turma.strip().lower()
        frequencias = [
            f for f in frequencias
            if f.aluno and f.aluno.turma and f.aluno.turma.strip().lower() == turma_normalizada
        ]
    
    alunos_stats = {}
    for f in frequencias:
        aluno = f.aluno
        if not aluno:
            continue
        nome = aluno.usuario.nome if aluno.usuario else "Sem nome"
        if nome not in alunos_stats:
            alunos_stats[nome] = {"presente": 0, "falta": 0, "justificada": 0, "turma": aluno.turma, "matricula": aluno.matricula}
        alunos_stats[nome][f.status] += 1
    
    for nome, stats in alunos_stats.items():
        total = stats["presente"] + stats["falta"] + stats["justificada"]
        stats["total"] = total
        stats["percentual"] = round((stats["presente"] / total) * 100, 1) if total > 0 else 0
    
    turmas = sorted(set(a.turma for a in Aluno.query.all() if a.turma))
    disciplinas = ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês", "Artes", "Educação Física"]
    
    return render_template(
        "frequencia/relatorio.html",
        alunos_stats=alunos_stats,
        turmas=turmas,
        disciplinas=disciplinas,
        turma_filtro=turma,
        disciplina_filtro=disciplina
    )