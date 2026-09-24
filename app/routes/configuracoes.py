from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db
from app.models.usuario import Usuario
from app.models.configuracao import Configuracao
import re

configuracoes_bp = Blueprint('configuracoes', __name__)

def get_config(usuario_id):
    """Retorna a config do usuário ou cria uma nova se não existir"""
    config = Configuracao.query.filter_by(usuario_id=usuario_id).first()
    if not config:
        config = Configuracao(usuario_id=usuario_id)
        db.session.add(config)
        db.session.commit()
    return config

@configuracoes_bp.route("/configuracoes")
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    usuario_id = session.get('usuario_id')
    usuario = Usuario.query.get(usuario_id)
    config = get_config(usuario_id)
    
    return render_template(
        "configuracoes/index.html",
        usuario=usuario,
        config=config
    )

# =========================
# API - SALVAR CONFIGURAÇÕES
# =========================
@configuracoes_bp.route("/api/configuracoes/salvar", methods=["POST"])
def salvar():
    if 'usuario_id' not in session:
        return jsonify({"ok": False, "error": "Não autorizado"}), 401
    
    usuario_id = session.get('usuario_id')
    config = get_config(usuario_id)
    
    data = request.get_json()
    
    if 'tema' in data:
        config.tema = data['tema']
    if 'cor_destaque' in data:
        cor = data['cor_destaque']
        if re.match(r'^#[0-9A-Fa-f]{6}$', cor):
            config.cor_destaque = cor
    if 'densidade' in data:
        config.densidade = data['densidade']
    if 'sidebar_recolhida' in data:
        config.sidebar_recolhida = bool(data['sidebar_recolhida'])
    if 'fonte' in data:
        config.fonte = data['fonte']
    if 'tamanho_fonte' in data:
        try:
            t = int(data['tamanho_fonte'])
            if 13 <= t <= 18:
                config.tamanho_fonte = t
        except:
            pass
    
    if 'notif_emprestimo' in data:
        config.notif_emprestimo = bool(data['notif_emprestimo'])
    if 'notif_nota' in data:
        config.notif_nota = bool(data['notif_nota'])
    if 'notif_falta' in data:
        config.notif_falta = bool(data['notif_falta'])
    
    if 'perfil_publico' in data:
        config.perfil_publico = bool(data['perfil_publico'])
    
    db.session.commit()
    return jsonify({"ok": True, "config": config.to_dict()})

# =========================
# API - OBTER CONFIGURAÇÕES (para aplicar no frontend)
# =========================
@configuracoes_bp.route("/api/configuracoes")
def obter():
    if 'usuario_id' not in session:
        return jsonify({
            "tema": "escuro",
            "cor_destaque": "#5865F2",
            "densidade": "confortavel",
            "sidebar_recolhida": False,
            "fonte": "Inter",
            "tamanho_fonte": 15
        })
    
    config = get_config(session.get('usuario_id'))
    return jsonify(config.to_dict())

# =========================
# ATUALIZAR DADOS DA CONTA
# =========================
@configuracoes_bp.route("/api/configuracoes/conta", methods=["POST"])
def atualizar_conta():
    if 'usuario_id' not in session:
        return jsonify({"ok": False}), 401
    
    usuario_id = session.get('usuario_id')
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"ok": False}), 404
    
    data = request.get_json()
    
    if data.get('nome'):
        usuario.nome = data['nome'].strip()
        session['usuario'] = usuario.nome
    
    if data.get('email'):
        novo_email = data['email'].strip().lower()
        # Verifica se o email já existe em outro usuário
        existente = Usuario.query.filter(
            Usuario.email == novo_email,
            Usuario.id != usuario_id
        ).first()
        if existente:
            return jsonify({"ok": False, "error": "Email já está em uso"}), 400
        usuario.email = novo_email
        session['email'] = usuario.email
    
    if data.get('nova_senha'):
        senha_atual = data.get('senha_atual', '')
        if not usuario.verificar_senha(senha_atual):
            return jsonify({"ok": False, "error": "Senha atual incorreta"}), 400
        nova = data['nova_senha']
        if len(nova) < 4:
            return jsonify({"ok": False, "error": "Nova senha muito curta"}), 400
        usuario.senha_criptografada = nova
    
    db.session.commit()
    return jsonify({"ok": True})