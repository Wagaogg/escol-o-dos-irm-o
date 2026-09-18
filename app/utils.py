import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

# =========================
# CONFIGURAÇÕES
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def formatar_data_br(data_str):
    if not data_str:
        return None
    try:
        if '/' in data_str:
            return data_str
        data_obj = datetime.strptime(data_str, "%Y-%m-%d")
        return data_obj.strftime("%d/%m/%Y")
    except:
        return data_str

def formatar_data_iso(data_str):
    if not data_str:
        return None
    try:
        if '-' in data_str:
            return data_str
        data_obj = datetime.strptime(data_str, "%d/%m/%Y")
        return data_obj.strftime("%Y-%m-%d")
    except:
        return data_str

# =========================
# CARREGAR / SALVAR JSON (temporário até migrar pro SQLite)
# =========================

def carregar_json(arquivo, padrao=None):
    if padrao is None:
        padrao = []
    caminho = os.path.join(DATA_DIR, arquivo)
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return list(padrao)

def salvar_json(arquivo, dados):
    caminho = os.path.join(DATA_DIR, arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# =========================
# ALUNOS (JSON)
# =========================
def carregar_alunos():
    from app.models.aluno import Aluno
    dados = carregar_json("alunos.json")
    return [Aluno.from_dict(a) for a in dados]

def salvar_alunos(alunos):
    dados = [a.to_dict() for a in alunos]
    salvar_json("alunos.json", dados)

# =========================
# PROFESSORES (JSON)
# =========================
def carregar_professores():
    from app.models.professor import Professor
    dados = carregar_json("professores.json")
    return [Professor.from_dict(p) for p in dados]

def salvar_professores(professores):
    dados = [p.to_dict() for p in professores]
    salvar_json("professores.json", dados)