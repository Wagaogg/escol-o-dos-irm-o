from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import os
from datetime import timedelta

# Inicializa extensões
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Configurações
    app.secret_key = os.environ.get('SECRET_KEY', 'sistema_escolar_2026')
    app.permanent_session_lifetime = timedelta(hours=1)
    
    # Banco de dados SQLite
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'escola.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Upload
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    
    # E-mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', '')
    
    # Inicializa extensões
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # Importa e registra os blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.alunos import alunos_bp
    from app.routes.professores import professores_bp
    from app.routes.biblioteca import biblioteca_bp
    from app.routes.notas import notas_bp
    from app.routes.meu_perfil import meu_perfil_bp
    
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(alunos_bp, url_prefix='/')
    app.register_blueprint(professores_bp, url_prefix='/')
    app.register_blueprint(biblioteca_bp, url_prefix='/')
    app.register_blueprint(notas_bp, url_prefix='/')
    app.register_blueprint(meu_perfil_bp, url_prefix='/')
    
    # Cria tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    return app