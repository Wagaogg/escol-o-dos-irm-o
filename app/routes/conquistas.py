from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from app import db
from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.livro import Livro
from app.models.frequencia import Frequencia
from app.models.conquista import Conquista, ConquistaVista
from app.utils_conquistas import (
    CONQUISTAS,
    RARIDADES,
    get_conquistas_por_publico,
)
import json
import re
from datetime import datetime


conquistas_bp = Blueprint('conquistas', __name__)


# =========================
# HELPERS
# =========================
def normalizar(texto):
    """Remove tudo que não for letra/número e minúsculo."""
    if not texto:
        return ""
    return re.sub(r'[^a-z0-9]', '', str(texto).lower())


def get_usuario_tipo(usuario_id):
    """Retorna 'aluno', 'professor' ou None."""
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return None
    if usuario.tipo == "professor":
        return "professor"
    if usuario.tipo == "aluno":
        return "aluno"
    return None


def get_publico_conquistas(usuario_id):
    """Retorna o dict de conquistas do público do usuário."""
    tipo = get_usuario_tipo(usuario_id)
    if tipo == "professor":
        return get_conquistas_por_publico("professor")
    return get_conquistas_por_publico("aluno")


# =========================
# DESBLOQUEAR
# =========================
def desbloquear(usuario_id, codigo):
    if codigo not in CONQUISTAS:
        return False
    existente = Conquista.query.filter_by(usuario_id=usuario_id, codigo=codigo).first()
    if existente:
        return False
    nova = Conquista(usuario_id=usuario_id, codigo=codigo)
    db.session.add(nova)
    return True


# =========================
# HELPERS DE CONTAGEM — ALUNO
# =========================
def _aluno_contar_livros(aluno):
    if not aluno or not aluno.usuario:
        return 0
    return Livro.query.filter(
        Livro.emprestado_para.isnot(None),
        db.func.lower(Livro.emprestado_para) == (aluno.usuario.nome or "").lower()
    ).count()


def _aluno_media_geral(aluno):
    if not aluno or not aluno.notas:
        return 0
    notas = json.loads(aluno.notas) if isinstance(aluno.notas, str) else aluno.notas
    disciplinas = set(n["disciplina"] for n in notas if n.get("disciplina"))
    medias = []
    for d in disciplinas:
        notas_d = [n["nota"] for n in notas if n.get("disciplina") == d]
        if len(notas_d) == 4:
            medias.append(sum(notas_d) / 4)
    return round(sum(medias) / len(medias), 2) if medias else 0


def _aluno_percentual_presenca(aluno):
    if not aluno:
        return 0
    freq = Frequencia.query.filter_by(aluno_id=aluno.id).all()
    total = len(freq)
    if total == 0:
        return 0
    presentes = len([f for f in freq if f.status == "presente"])
    return round((presentes / total) * 100, 1)


def _aluno_posicao_ranking(aluno):
    todos = Aluno.query.all()
    ranking = [(a.id, calcular_pontos(a)) for a in todos]
    ranking = sorted(ranking, key=lambda x: x[1], reverse=True)
    return next((i for i, (aid, _) in enumerate(ranking, 1) if aid == aluno.id), 999)


# =========================
# HELPERS DE CONTAGEM — PROFESSOR
# =========================
def _prof_notas_lancadas(prof):
    """Conta notas nos alunos das turmas do professor."""
    if not prof or not prof.turmas_lista:
        return 0
    try:
        turmas = json.loads(prof.turmas_lista)
    except Exception:
        turmas = []
    turmas_norm = [normalizar(t) for t in turmas if t]
    if not turmas_norm:
        return 0
    total = 0
    for aluno in Aluno.query.all():
        if aluno.turma and normalizar(aluno.turma) in turmas_norm:
            notas = json.loads(aluno.notas) if aluno.notas else []
            total += len(notas)
    return total


def _prof_chamadas_feitas(prof):
    if not prof:
        return 0
    return Frequencia.query.filter_by(professor_id=prof.id).count()


def _prof_turmas_count(prof):
    if not prof or not prof.turmas_lista:
        return 0
    try:
        return len(json.loads(prof.turmas_lista))
    except Exception:
        return 0


# =========================
# PONTOS (usado no ranking e em conquistas de ranking)
# =========================
def calcular_pontos(aluno):
    usuario = aluno.usuario
    if not usuario:
        return 0
    media_geral = _aluno_media_geral(aluno)
    pct = _aluno_percentual_presenca(aluno)
    livros = _aluno_contar_livros(aluno)
    pontos = 0
    if media_geral > 0:
        pontos += (media_geral / 10) * 50
    pontos += (pct / 100) * 30
    pontos += min(livros * 5, 20)
    return round(pontos, 1)


# =========================
# VERIFICAR CONQUISTAS — ALUNO
# =========================
def verificar_conquistas_aluno(usuario_id):
    aluno = Aluno.query.filter_by(usuario_id=usuario_id).first()
    if not aluno:
        return []
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return []

    novas = []

    # Biblioteca
    livros = _aluno_contar_livros(aluno)
    if livros >= 1 and desbloquear(usuario_id, "primeiro_emprestimo"):
        novas.append("primeiro_emprestimo")
    if livros >= 5 and desbloquear(usuario_id, "leitor_dedicado"):
        novas.append("leitor_dedicado")
    if livros >= 10 and desbloquear(usuario_id, "rato_de_biblioteca"):
        novas.append("rato_de_biblioteca")
    if livros >= 20 and desbloquear(usuario_id, "devorador_de_livros"):
        novas.append("devorador_de_livros")

    # Notas
    notas = json.loads(aluno.notas) if aluno.notas else []
    if len(notas) >= 1 and desbloquear(usuario_id, "primeira_nota"):
        novas.append("primeira_nota")
    if any(n.get("nota", 0) >= 10 for n in notas) and desbloquear(usuario_id, "nota_perfeita"):
        novas.append("nota_perfeita")

    media = _aluno_media_geral(aluno)
    if media >= 6 and desbloquear(usuario_id, "aprovado"):
        novas.append("aprovado")
    if media >= 9 and desbloquear(usuario_id, "aluno_destaque"):
        novas.append("aluno_destaque")

    # Frequência
    freq = Frequencia.query.filter_by(aluno_id=aluno.id).all()
    if len(freq) >= 1 and desbloquear(usuario_id, "primeira_presenca"):
        novas.append("primeira_presenca")

    pct = _aluno_percentual_presenca(aluno)
    if pct >= 75 and desbloquear(usuario_id, "frequente"):
        novas.append("frequente")
    if pct == 100 and len(freq) > 0 and desbloquear(usuario_id, "presenca_perfeita"):
        novas.append("presenca_perfeita")

    # Madrugada
    hora = datetime.now().hour
    if hora < 6 and desbloquear(usuario_id, "madrugador"):
        novas.append("madrugador")
    if hora >= 23 and desbloquear(usuario_id, "coruja"):
        novas.append("coruja")

    # Ranking
    posicao = _aluno_posicao_ranking(aluno)
    if posicao == 1 and desbloquear(usuario_id, "rank_top1"):
        novas.append("rank_top1")
    if posicao <= 3 and desbloquear(usuario_id, "rank_top3"):
        novas.append("rank_top3")

    # Veterano
    if usuario.criado_em:
        dias = (datetime.utcnow() - usuario.criado_em).days
        if dias >= 30 and desbloquear(usuario_id, "veterano"):
            novas.append("veterano")

    db.session.commit()
    return novas


# =========================
# VERIFICAR CONQUISTAS — PROFESSOR
# =========================
def verificar_conquistas_professor(usuario_id):
    prof = Professor.query.filter_by(usuario_id=usuario_id).first()
    if not prof:
        return []
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return []

    novas = []

    # Sempre desbloqueia "primeiro_acesso" ao logar
    if desbloquear(usuario_id, "primeiro_acesso"):
        novas.append("primeiro_acesso")

    # Notas
    notas_lancadas = _prof_notas_lancadas(prof)
    if notas_lancadas >= 1 and desbloquear(usuario_id, "primeira_nota_lancada"):
        novas.append("primeira_nota_lancada")
    if notas_lancadas >= 20 and desbloquear(usuario_id, "professor_atento"):
        novas.append("professor_atento")
    if notas_lancadas >= 100 and desbloquear(usuario_id, "mestre_das_notas"):
        novas.append("mestre_das_notas")
    if notas_lancadas >= 500 and desbloquear(usuario_id, "senhor_do_boletim"):
        novas.append("senhor_do_boletim")

    # Chamadas
    chamadas = _prof_chamadas_feitas(prof)
    if chamadas >= 1 and desbloquear(usuario_id, "primeira_chamada"):
        novas.append("primeira_chamada")
    if chamadas >= 10 and desbloquear(usuario_id, "professor_presente"):
        novas.append("professor_presente")
    if chamadas >= 50 and desbloquear(usuario_id, "mestre_da_chamada"):
        novas.append("mestre_da_chamada")
    if chamadas >= 100 and desbloquear(usuario_id, "lenda_da_frequencia"):
        novas.append("lenda_da_frequencia")

    # Turmas
    turmas = _prof_turmas_count(prof)
    if turmas >= 1 and desbloquear(usuario_id, "primeira_turma"):
        novas.append("primeira_turma")
    if turmas >= 3 and desbloquear(usuario_id, "multitarefas"):
        novas.append("multitarefas")
    if turmas >= 5 and desbloquear(usuario_id, "super_professor"):
        novas.append("super_professor")

    # Madrugada
    hora = datetime.now().hour
    if hora < 6 and desbloquear(usuario_id, "madrugador_professor"):
        novas.append("madrugador_professor")
    if hora >= 23 and desbloquear(usuario_id, "coruja_professor"):
        novas.append("coruja_professor")

    # Dedicado: 10 chamadas E 20 notas
    if chamadas >= 10 and notas_lancadas >= 20 and desbloquear(usuario_id, "dedicado"):
        novas.append("dedicado")

    # Veterano / Lendário
    if usuario.criado_em:
        dias = (datetime.utcnow() - usuario.criado_em).days
        if dias >= 60 and desbloquear(usuario_id, "professor_veterano"):
            novas.append("professor_veterano")
        if dias >= 180 and desbloquear(usuario_id, "professor_lendario"):
            novas.append("professor_lendario")

    db.session.commit()
    return novas


# =========================
# DISPATCHER
# =========================
def verificar_conquistas(usuario_id):
    """Chama a verificação correta conforme o tipo do usuário."""
    tipo = get_usuario_tipo(usuario_id)
    if tipo == "aluno":
        return verificar_conquistas_aluno(usuario_id)
    if tipo == "professor":
        return verificar_conquistas_professor(usuario_id)
    return []


# =========================
# PROGRESSO — ALUNO
# =========================
def calcular_progresso_aluno(aluno, codigo):
    info = CONQUISTAS.get(codigo)
    if not info:
        return (0, 1)

    meta = info["meta"]
    tipo = info["tipo"]
    usuario = aluno.usuario

    if tipo == "livros":
        atual = _aluno_contar_livros(aluno)
    elif tipo == "notas":
        notas = json.loads(aluno.notas) if aluno.notas else []
        atual = len(notas)
    elif tipo == "nota_dez":
        notas = json.loads(aluno.notas) if aluno.notas else []
        atual = 1 if any(n.get("nota", 0) >= 10 for n in notas) else 0
    elif tipo == "media":
        atual = int(_aluno_media_geral(aluno))
    elif tipo == "presencas":
        atual = Frequencia.query.filter_by(aluno_id=aluno.id).count()
    elif tipo == "percentual_presenca":
        atual = int(_aluno_percentual_presenca(aluno))
    elif tipo == "dias":
        atual = (datetime.utcnow() - usuario.criado_em).days if usuario.criado_em else 0
    elif tipo == "rank":
        posicao = _aluno_posicao_ranking(aluno)
        if codigo == "rank_top1":
            atual = 1 if posicao == 1 else 0
        else:
            atual = 1 if posicao <= 3 else 0
    else:
        atual = 0

    return (min(atual, meta), meta)


# =========================
# PROGRESSO — PROFESSOR
# =========================
def calcular_progresso_professor(prof, codigo):
    info = CONQUISTAS.get(codigo)
    if not info:
        return (0, 1)

    meta = info["meta"]
    tipo = info["tipo"]
    usuario = prof.usuario

    if tipo == "notas_lancadas":
        atual = _prof_notas_lancadas(prof)
    elif tipo == "chamadas_feitas":
        atual = _prof_chamadas_feitas(prof)
    elif tipo == "turmas":
        atual = _prof_turmas_count(prof)
    elif tipo == "dias":
        atual = (datetime.utcnow() - usuario.criado_em).days if usuario.criado_em and usuario.criado_em else 0
    elif tipo == "primeiro_login":
        atual = 1
    elif tipo == "dedicado":
        atual = 1 if (_prof_chamadas_feitas(prof) >= 10 and _prof_notas_lancadas(prof) >= 20) else 0
    else:
        atual = 0

    return (min(atual, meta), meta)


# =========================
# PÁGINA DE CONQUISTAS
# =========================
@conquistas_bp.route("/conquistas")
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    usuario_id = session.get('usuario_id')
    tipo = get_usuario_tipo(usuario_id)

    if tipo not in ("aluno", "professor"):
        flash("Conquistas disponíveis apenas para alunos e professores.", "warning")
        return redirect(url_for('dashboard.index'))

    verificar_conquistas(usuario_id)

    aluno = Aluno.query.filter_by(usuario_id=usuario_id).first() if tipo == "aluno" else None
    professor = Professor.query.filter_by(usuario_id=usuario_id).first() if tipo == "professor" else None

    minhas = Conquista.query.filter_by(usuario_id=usuario_id).all()
    codigos_desbloqueados = {c.codigo: c.desbloqueada_em for c in minhas}

    total_usuarios = Usuario.query.count() or 1

    # 🔥 Só as conquistas do público do usuário
    conquistas_do_publico = get_publico_conquistas(usuario_id)

    lista = []
    for codigo, info in conquistas_do_publico.items():
        desbloqueada = codigo in codigos_desbloqueados

        if info.get("secreta") and not desbloqueada:
            continue

        atual, meta = (0, info["meta"])
        if aluno:
            atual, meta = calcular_progresso_aluno(aluno, codigo)
        elif professor:
            atual, meta = calcular_progresso_professor(professor, codigo)

        qtd_tem = Conquista.query.filter_by(codigo=codigo).count()
        percentual_tem = round((qtd_tem / total_usuarios) * 100, 1)

        lista.append({
            "codigo": codigo,
            "nome": info["nome"],
            "descricao": info["descricao"],
            "detalhamento": info.get("detalhamento", ""),
            "icone": info["icone"],
            "categoria": info["categoria"],
            "raridade": info.get("raridade", "comum"),
            "raridade_info": RARIDADES.get(info.get("raridade", "comum"), RARIDADES["comum"]),
            "desbloqueada": desbloqueada,
            "data": codigos_desbloqueados.get(codigo),
            "progresso_atual": atual,
            "progresso_meta": meta,
            "progresso_percentual": round((atual / meta) * 100) if meta > 0 else 0,
            "percentual_usuarios": percentual_tem,
            "qtd_usuarios": qtd_tem,
        })

    categorias = {}
    for c in lista:
        categorias.setdefault(c["categoria"], []).append(c)

    total = len(lista)
    desbloqueadas = len([c for c in lista if c["desbloqueada"]])
    percentual = round((desbloqueadas / total) * 100) if total > 0 else 0

    return render_template(
        "conquistas/index.html",
        categorias=categorias,
        total=total,
        desbloqueadas=desbloqueadas,
        percentual=percentual,
        tipo=tipo,
    )


# =========================
# PÁGINA DE UMA CONQUISTA
# =========================
@conquistas_bp.route("/conquistas/<codigo>")
def detalhe(codigo):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    usuario_id = session.get('usuario_id')
    tipo = get_usuario_tipo(usuario_id)

    info = CONQUISTAS.get(codigo)
    if not info:
        flash("Conquista não encontrada.", "danger")
        return redirect(url_for('conquistas.index'))

    # 🔒 Garante que o usuário só veja conquistas do seu público
    if info.get("publico") != tipo:
        flash("Essa conquista não pertence ao seu perfil.", "warning")
        return redirect(url_for('conquistas.index'))

    # Se for secreta e ainda não desbloqueada, esconde
    ja_tem = Conquista.query.filter_by(usuario_id=usuario_id, codigo=codigo).first()
    if info.get("secreta") and not ja_tem:
        flash("Conquista secreta — continue jogando.", "info")
        return redirect(url_for('conquistas.index'))

    conquistas_db = Conquista.query.filter_by(codigo=codigo).order_by(Conquista.desbloqueada_em.asc()).all()
    usuarios_com = []
    for c in conquistas_db:
        u = Usuario.query.get(c.usuario_id)
        if u:
            usuarios_com.append({"nome": u.nome, "foto": u.foto, "data": c.desbloqueada_em})

    total_usuarios = Usuario.query.count() or 1
    percentual = round((len(usuarios_com) / total_usuarios) * 100, 1)

    return render_template(
        "conquistas/detalhe.html",
        info=info,
        codigo=codigo,
        raridade_info=RARIDADES.get(info.get("raridade", "comum"), RARIDADES["comum"]),
        usuarios_com=usuarios_com,
        percentual=percentual,
        primeiro=usuarios_com[0] if usuarios_com else None
    )


# =========================
# API - NOVAS (toast)
# =========================
@conquistas_bp.route("/api/conquistas/novas")
def api_novas():
    if 'usuario_id' not in session:
        return jsonify({"novas": []})

    usuario_id = session.get('usuario_id')
    tipo = get_usuario_tipo(usuario_id)
    if tipo not in ("aluno", "professor"):
        return jsonify({"novas": []})

    publico = get_publico_conquistas(usuario_id)

    subquery = db.session.query(ConquistaVista.conquista_id).filter_by(usuario_id=usuario_id)
    novas = Conquista.query.filter(
        Conquista.usuario_id == usuario_id,
        ~Conquista.id.in_(subquery)
    ).all()

    resultado = []
    for c in novas:
        # Só retorna se pertencer ao público do usuário
        info = publico.get(c.codigo)
        if not info:
            continue
        resultado.append({
            "id": c.id,
            "codigo": c.codigo,
            "nome": info["nome"],
            "descricao": info["descricao"],
            "detalhamento": info.get("detalhamento", ""),
            "icone": info["icone"],
            "raridade": info.get("raridade", "comum"),
            "raridade_info": RARIDADES.get(info.get("raridade", "comum"), RARIDADES["comum"]),
        })

    return jsonify({"novas": resultado})


# =========================
# API - MARCAR COMO VISTA
# =========================
@conquistas_bp.route("/api/conquistas/<int:conquista_id>/vista", methods=["POST"])
def api_marcar_vista(conquista_id):
    if 'usuario_id' not in session:
        return jsonify({"ok": False}), 401

    usuario_id = session.get('usuario_id')
    nova = ConquistaVista(usuario_id=usuario_id, conquista_id=conquista_id)
    db.session.add(nova)
    db.session.commit()
    return jsonify({"ok": True})