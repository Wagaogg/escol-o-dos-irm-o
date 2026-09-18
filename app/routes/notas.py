from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.usuario import Usuario
from app.models.notificacao import Notificacao
from app.models.frequencia import Frequencia
from datetime import datetime
import json

notas_bp = Blueprint('notas', __name__)

# =========================
# PERMISSÕES
# =========================
def is_admin():
    return session.get("tipo") in ["admin", "diretor"]

def is_staff():
    return session.get("tipo") in ["admin", "diretor", "professor"]

def is_professor():
    return session.get("tipo") == "professor"

def is_aluno():
    return session.get("tipo") == "aluno"

# =========================
# LANÇAR NOTA
# =========================
@notas_bp.route("/notas/lancar", methods=["GET", "POST"])
def lancar_nota():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if not is_professor():
        flash("Apenas professores podem lançar notas.", "danger")
        return redirect(url_for('dashboard.index'))
    
    if request.method == "POST":
        aluno_id = request.form.get("aluno_id")
        disciplina = request.form.get("disciplina")
        bimestre = request.form.get("bimestre")
        nota = request.form.get("nota")
        
        if not all([aluno_id, disciplina, bimestre, nota]):
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for('notas.lancar_nota'))
        
        try:
            bimestre = int(bimestre)
            if bimestre < 1 or bimestre > 4:
                flash("Bimestre deve ser entre 1 e 4.", "danger")
                return redirect(url_for('notas.lancar_nota'))
            nota = float(nota)
            if nota < 0 or nota > 10:
                flash("Nota deve ser entre 0 e 10.", "danger")
                return redirect(url_for('notas.lancar_nota'))
        except:
            flash("Valores inválidos.", "danger")
            return redirect(url_for('notas.lancar_nota'))
        
        aluno = Aluno.query.get(int(aluno_id))
        if not aluno:
            flash("Aluno não encontrado.", "danger")
            return redirect(url_for('notas.lancar_nota'))
        
        notas = json.loads(aluno.notas) if aluno.notas else []
        
        # Verifica duplicata
        for n in notas:
            if n.get("disciplina", "").lower() == disciplina.lower() and n.get("bimestre") == bimestre:
                flash(f"Já existe nota para {disciplina} no {bimestre}º bimestre.", "warning")
                return redirect(url_for('notas.lancar_nota'))
        
        notas.append({
            "disciplina": disciplina,
            "bimestre": bimestre,
            "nota": nota
        })
        
        aluno.notas = json.dumps(notas)
        db.session.commit()
        
        flash(f"✅ Nota {nota} lançada para {aluno.usuario.nome} em {disciplina} ({bimestre}º bimestre).", "success")
        
        # Notificação
        notif = Notificacao(
            usuario_id=aluno.usuario_id,
            mensagem=f"Nota lançada em {disciplina} ({bimestre}º bimestre): {nota}",
            link=url_for('notas.boletim', aluno_id=aluno.id)
        )
        db.session.add(notif)
        db.session.commit()
        
        return redirect(url_for('notas.lancar_nota'))
    
    # GET
    alunos = Aluno.query.all()
    disciplinas = ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês", "Artes", "Educação Física"]
    bimestres = [1, 2, 3, 4]
    
    alunos_com_nome = []
    for a in alunos:
        alunos_com_nome.append({
            "id": a.id,
            "nome": a.usuario.nome if a.usuario else "Sem nome",
            "matricula": a.matricula,
            "turma": a.turma
        })
    
    return render_template("notas/lancar.html", alunos=alunos_com_nome, disciplinas=disciplinas, bimestres=bimestres)

# =========================
# BOLETIM (ALUNO) - COMPLETO COM NOTAS + FREQUÊNCIA
# =========================
@notas_bp.route("/boletim/<int:aluno_id>")
def boletim(aluno_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    # Permissões
    if is_aluno():
        usuario_id = session.get('usuario_id')
        aluno_logado = Aluno.query.filter_by(usuario_id=usuario_id).first()
        if not aluno_logado or aluno_logado.id != aluno_id:
            flash("Você só pode ver seu próprio boletim.", "danger")
            return redirect(url_for('dashboard.index'))
    elif not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.index'))
    
    # =========================
    # NOTAS
    # =========================
    notas = json.loads(aluno.notas) if aluno.notas else []
    
    disciplinas = sorted(set(n["disciplina"] for n in notas))
    dados_notas = {}
    for d in disciplinas:
        dados_notas[d] = {1: None, 2: None, 3: None, 4: None}
        for n in notas:
            if n["disciplina"] == d:
                bim = n.get("bimestre", 1)
                if 1 <= bim <= 4:
                    dados_notas[d][bim] = n["nota"]
    
    # =========================
    # FREQUÊNCIA
    # =========================
    frequencias = Frequencia.query.filter_by(aluno_id=aluno.id).all()
    freq_por_disciplina = {}
    for f in frequencias:
        if f.disciplina not in freq_por_disciplina:
            freq_por_disciplina[f.disciplina] = {"presente": 0, "falta": 0, "justificada": 0}
        freq_por_disciplina[f.disciplina][f.status] += 1
    
    # =========================
    # MÉDIAS E SITUAÇÃO
    # =========================
    resultado = {}
    for d in disciplinas:
        # Média das notas (só se tiver as 4)
        notas_d = [dados_notas[d][b] for b in [1, 2, 3, 4] if dados_notas[d][b] is not None]
        
        if len(notas_d) == 4:
            media = round(sum(notas_d) / 4, 2)
        else:
            media = None
        
        # Frequência
        freq = freq_por_disciplina.get(d, {"presente": 0, "falta": 0, "justificada": 0})
        total_aulas = freq["presente"] + freq["falta"] + freq["justificada"]
        percentual_presenca = round((freq["presente"] / total_aulas) * 100, 1) if total_aulas > 0 else None
        
        # Situação
        situacao = None
        if media is not None:
            if media >= 6 and (percentual_presenca is None or percentual_presenca >= 75):
                situacao = "Aprovado"
            elif media >= 6 and percentual_presenca is not None and percentual_presenca < 75:
                situacao = "Reprovado por Falta"
            else:
                situacao = "Reprovado"
        
        resultado[d] = {
            "bimestres": dados_notas[d],
            "media": media,
            "frequencia": freq,
            "total_aulas": total_aulas,
            "percentual_presenca": percentual_presenca,
            "situacao": situacao
        }
    
    # Média geral (só disciplinas completas)
    medias_validas = [r["media"] for r in resultado.values() if r["media"] is not None]
    media_geral = round(sum(medias_validas) / len(medias_validas), 2) if medias_validas else None
    
    # Frequência geral
    total_aulas_geral = sum(f["presente"] + f["falta"] + f["justificada"] for f in freq_por_disciplina.values())
    total_presentes_geral = sum(f["presente"] for f in freq_por_disciplina.values())
    percentual_geral = round((total_presentes_geral / total_aulas_geral) * 100, 1) if total_aulas_geral > 0 else None
    
    # Situação geral
    situacao_geral = None
    if media_geral is not None:
        if media_geral >= 6 and (percentual_geral is None or percentual_geral >= 75):
            situacao_geral = "Aprovado"
        else:
            situacao_geral = "Reprovado"
    
    # Dados do aluno
    aluno_info = {
        "id": aluno.id,
        "nome": aluno.usuario.nome if aluno.usuario else "Sem nome",
        "matricula": aluno.matricula,
        "turma": aluno.turma,
        "serie": aluno.serie,
        "email": aluno.usuario.email if aluno.usuario else "",
        "foto": aluno.usuario.foto if aluno.usuario else None
    }
    
    return render_template(
        "notas/boletim.html",
        aluno=aluno_info,
        resultado=resultado,
        disciplinas=disciplinas,
        media_geral=media_geral,
        percentual_geral=percentual_geral,
        situacao_geral=situacao_geral,
        total_aulas_geral=total_aulas_geral,
        total_presentes_geral=total_presentes_geral
    )