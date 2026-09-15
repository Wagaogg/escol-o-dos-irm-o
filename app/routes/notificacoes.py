from flask import Blueprint, render_template, redirect, url_for, session, jsonify, flash
from app import db
from app.models.notificacao import Notificacao

notificacoes_bp = Blueprint('notificacoes', __name__)

# =========================
# PÁGINA DE NOTIFICAÇÕES
# =========================
@notificacoes_bp.route("/notificacoes")
def listar():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    usuario_id = session.get('usuario_id')
    notificacoes = Notificacao.query.filter_by(usuario_id=usuario_id).order_by(Notificacao.criada_em.desc()).all()
    
    # Marca todas como lidas ao abrir a página
    for n in notificacoes:
        n.lida = True
    db.session.commit()
    
    return render_template("notificacoes/listar.html", notificacoes=notificacoes)

# =========================
# API - CONTAR NÃO LIDAS
# =========================
@notificacoes_bp.route("/api/notificacoes/contar")
def contar():
    if 'usuario_id' not in session:
        return jsonify({"total": 0})
    
    usuario_id = session.get('usuario_id')
    total = Notificacao.query.filter_by(usuario_id=usuario_id, lida=False).count()
    return jsonify({"total": total})

# =========================
# API - LISTAR NÃO LIDAS (para dropdown)
# =========================
@notificacoes_bp.route("/api/notificacoes")
def api_listar():
    if 'usuario_id' not in session:
        return jsonify({"notificacoes": []})
    
    usuario_id = session.get('usuario_id')
    notificacoes = Notificacao.query.filter_by(usuario_id=usuario_id).order_by(Notificacao.criada_em.desc()).limit(10).all()
    return jsonify({"notificacoes": [n.to_dict() for n in notificacoes]})

# =========================
# MARCAR COMO LIDA
# =========================
@notificacoes_bp.route("/notificacoes/<int:notif_id>/marcar_lida", methods=["POST"])
def marcar_lida(notif_id):
    if 'usuario_id' not in session:
        return jsonify({"ok": False}), 401
    
    notif = Notificacao.query.get(notif_id)
    if notif and notif.usuario_id == session.get('usuario_id'):
        notif.lida = True
        db.session.commit()
        return jsonify({"ok": True})
    
    return jsonify({"ok": False}), 404