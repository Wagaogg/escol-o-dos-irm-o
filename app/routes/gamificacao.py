from flask import Blueprint, render_template, session, redirect, url_for, flash
from app import db
from app.models.aluno import Aluno
from app.models.frequencia import Frequencia
from app.models.livro import Livro
import json

gamificacao_bp = Blueprint('gamificacao', __name__)


def is_staff():
    return session.get("tipo") in ["admin", "diretor", "professor"]

def is_aluno():
    return session.get("tipo") == "aluno"


@gamificacao_bp.route("/ranking")
def ranking():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    # 🔥 VERIFICA CONQUISTAS ANTES DE MOSTRAR O RANKING
    try:
        from app.routes.conquistas import verificar_conquistas
        verificar_conquistas(session.get('usuario_id'))
    except Exception as e:
        print(f"Erro ao verificar conquistas: {e}")
    
    # Calcula o ranking
    alunos = Aluno.query.all()
    ranking = []
    
    for aluno in alunos:
        usuario = aluno.usuario
        if not usuario:
            continue
        
        # Notas
        notas = json.loads(aluno.notas) if aluno.notas else []
        disciplinas = set(n["disciplina"] for n in notas)
        medias = []
        for d in disciplinas:
            notas_d = [n["nota"] for n in notas if n["disciplina"] == d]
            if len(notas_d) == 4:
                medias.append(sum(notas_d) / 4)
        media_geral = round(sum(medias) / len(medias), 2) if medias else 0
        
        # Frequência
        freq = Frequencia.query.filter_by(aluno_id=aluno.id).all()
        total_freq = len(freq)
        presentes = len([f for f in freq if f.status == "presente"])
        percentual_presenca = round((presentes / total_freq) * 100, 1) if total_freq > 0 else 0
        
        # Livros emprestados
        livros_emprestados = Livro.query.filter(
            Livro.emprestado_para.isnot(None),
            db.func.lower(Livro.emprestado_para) == (usuario.nome or "").lower()
        ).count()
        
        # Pontuação
        pontos = 0
        if media_geral > 0:
            pontos += (media_geral / 10) * 50
        pontos += (percentual_presenca / 100) * 30
        pontos += min(livros_emprestados * 5, 20)
        pontos = round(pontos, 1)
        
        # Badges
        badges = []
        if media_geral >= 9:
            badges.append({"emoji": "🏆", "nome": "Excelência Acadêmica"})
        if percentual_presenca >= 95:
            badges.append({"emoji": "🎯", "nome": "Presença Perfeita"})
        if livros_emprestados >= 5:
            badges.append({"emoji": "📚", "nome": "Leitor Dedicado"})
        if media_geral >= 7 and percentual_presenca >= 85:
            badges.append({"emoji": "⭐", "nome": "Aluno Destaque"})
        
        ranking.append({
            "id": aluno.id,
            "nome": usuario.nome,
            "turma": aluno.turma,
            "foto": usuario.foto,
            "media": media_geral,
            "presenca": percentual_presenca,
            "livros": livros_emprestados,
            "pontos": pontos,
            "badges": badges
        })
    
    # Ordena por pontos
    ranking = sorted(ranking, key=lambda x: x["pontos"], reverse=True)
    
    # Adiciona posição
    for i, r in enumerate(ranking, 1):
        r["posicao"] = i
    
    return render_template("gamificacao/ranking.html", ranking=ranking)