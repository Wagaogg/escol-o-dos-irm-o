from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils import carregar_alunos, salvar_alunos

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
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    if not is_professor():
        flash("Apenas professores podem lançar notas.", "danger")
        return redirect(url_for('dashboard.home'))
    
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
        
        alunos = carregar_alunos()
        aluno = next((a for a in alunos if a.id == int(aluno_id)), None)
        if not aluno:
            flash("Aluno não encontrado.", "danger")
            return redirect(url_for('notas.lancar_nota'))
        
        # Verifica se já existe nota para essa disciplina e bimestre
        for n in aluno.notas:
            if n.get("disciplina", "").lower() == disciplina.lower() and n.get("bimestre") == bimestre:
                flash(f"Já existe nota para {disciplina} no {bimestre}º bimestre.", "warning")
                return redirect(url_for('notas.lancar_nota'))
        
        aluno.adicionar_nota(disciplina, bimestre, nota)
        salvar_alunos(alunos)
        flash(f"Nota {nota} lançada para {aluno.nome} em {disciplina} ({bimestre}º bimestre).", "success")
        return redirect(url_for('notas.lancar_nota'))
    
    # GET - exibe o formulário
    alunos = carregar_alunos()
    disciplinas = ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês", "Artes", "Educação Física"]
    bimestres = [1, 2, 3, 4]
    return render_template("notas/lancar.html", alunos=alunos, disciplinas=disciplinas, bimestres=bimestres)

# =========================
# BOLETIM
# =========================
@notas_bp.route("/boletim/<int:aluno_id>")
def boletim(aluno_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    alunos = carregar_alunos()
    aluno = next((a for a in alunos if a.id == aluno_id), None)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for('dashboard.home'))
    
    # Permissões
    if is_aluno():
        email = session.get("email", "")
        aluno_logado = next((a for a in alunos if (a.email or "").lower() == email.lower()), None)
        if not aluno_logado or aluno_logado.id != aluno_id:
            flash("Você só pode ver seu próprio boletim.", "danger")
            return redirect(url_for('dashboard.home'))
    elif not is_staff():
        flash("Acesso negado.", "danger")
        return redirect(url_for('dashboard.home'))
    
    # Organiza notas por disciplina e bimestre
    disciplinas = sorted(set(n["disciplina"] for n in aluno.notas))
    dados_notas = {}
    for d in disciplinas:
        dados_notas[d] = {1: None, 2: None, 3: None, 4: None}
        for n in aluno.notas:
            if n["disciplina"] == d:
                bim = n.get("bimestre", 1)
                if 1 <= bim <= 4:
                    dados_notas[d][bim] = n["nota"]
    
    # Calcula médias
    medias_disciplinas = {}
    for d in disciplinas:
        medias_disciplinas[d] = aluno.calcular_media_disciplina(d)
    
    media_geral = aluno.calcular_media_geral()
    situacao = None
    if media_geral is not None:
        situacao = "Aprovado" if media_geral >= 6 else "Reprovado"
    
    return render_template(
        "notas/boletim.html",
        aluno=aluno,
        dados_notas=dados_notas,
        medias_disciplinas=medias_disciplinas,
        media_geral=media_geral,
        situacao=situacao,
        tipo_usuario=session.get("tipo")
    )