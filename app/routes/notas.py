from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.aluno import Aluno
from app.models.professor import Professor
from datetime import datetime
import json

# =========================
# BLUEPRINT
# =========================
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
        
        # Carrega notas do JSON
        notas = json.loads(aluno.notas) if aluno.notas else []
        
        # Verifica duplicata
        for n in notas:
            if n.get("disciplina", "").lower() == disciplina.lower() and n.get("bimestre") == bimestre:
                flash(f"Já existe nota para {disciplina} no {bimestre}º bimestre.", "warning")
                return redirect(url_for('notas.lancar_nota'))
        
        # Adiciona nova nota
        notas.append({
            "disciplina": disciplina,
            "bimestre": bimestre,
            "nota": nota
        })
        
        aluno.notas = json.dumps(notas)
        db.session.commit()
        
        flash(f"Nota {nota} lançada para {aluno.usuario.nome} em {disciplina} ({bimestre}º bimestre).", "success")
        return redirect(url_for('notas.lancar_nota'))
    
    # GET - exibe o formulário
    alunos = Aluno.query.all()
    disciplinas = ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês", "Artes", "Educação Física"]
    bimestres = [1, 2, 3, 4]
    
    alunos_com_nome = []
    for a in alunos:
        alunos_com_nome.append({
            "id": a.id,
            "nome": a.usuario.nome if a.usuario else "Sem nome",
            "matricula": a.matricula
        })
    
    return render_template("notas/lancar.html", alunos=alunos_com_nome, disciplinas=disciplinas, bimestres=bimestres)

# =========================
# BOLETIM
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
    
    # Carrega notas do JSON
    notas = json.loads(aluno.notas) if aluno.notas else []
    
    # Organiza notas por disciplina e bimestre
    disciplinas = sorted(set(n["disciplina"] for n in notas))
    dados_notas = {}
    for d in disciplinas:
        dados_notas[d] = {1: None, 2: None, 3: None, 4: None}
        for n in notas:
            if n["disciplina"] == d:
                bim = n.get("bimestre", 1)
                if 1 <= bim <= 4:
                    dados_notas[d][bim] = n["nota"]
    
    # Calcula médias das disciplinas
    medias_disciplinas = {}
    for d in disciplinas:
        notas_d = [n["nota"] for n in notas if n["disciplina"] == d]
        if len(notas_d) == 4:
            medias_disciplinas[d] = round(sum(notas_d) / 4, 2)
        else:
            medias_disciplinas[d] = None
    
    # Média geral (apenas disciplinas completas)
    medias_validas = [m for m in medias_disciplinas.values() if m is not None]
    media_geral = round(sum(medias_validas) / len(medias_validas), 2) if medias_validas else None
    
    situacao = None
    if media_geral is not None:
        situacao = "Aprovado" if media_geral >= 6 else "Reprovado"
    
    # Dados do aluno para o template
    aluno_info = {
        "id": aluno.id,
        "nome": aluno.usuario.nome if aluno.usuario else "Sem nome",
        "matricula": aluno.matricula,
        "turma": aluno.turma,
        "email": aluno.usuario.email if aluno.usuario else "",
        "foto": aluno.usuario.foto if aluno.usuario else None
    }
    
    return render_template(
        "notas/boletim.html",
        aluno=aluno_info,
        dados_notas=dados_notas,
        medias_disciplinas=medias_disciplinas,
        media_geral=media_geral,
        situacao=situacao,
        tipo_usuario=session.get("tipo")
    )