# ============================================
# DEFINIÇÃO DAS CONQUISTAS
# ============================================
# Cada conquista tem:
#   nome, descricao (curta), detalhamento (longa),
#   icone, categoria, raridade, secreta,
#   meta (número-alvo), tipo (como calcular), publico (aluno/professor)


# ============================================
# CONQUISTAS DE ALUNO
# ============================================
CONQUISTAS_ALUNO = {

    # -------- BIBLIOTECA --------
    "primeiro_emprestimo": {
        "nome": "Primeiro Empréstimo",
        "descricao": "Emprestou seu primeiro livro",
        "detalhamento": (
            "Vá em Biblioteca, escolha um livro com estoque disponível e clique em "
            "'Emprestar'. Confirme o empréstimo no modal. Você só pode ter 1 livro "
            "emprestado por vez, então devolva antes de pegar outro."
        ),
        "icone": "📖",
        "categoria": "Biblioteca",
        "raridade": "comum",
        "secreta": False,
        "meta": 1,
        "tipo": "livros",
        "publico": "aluno",
    },
    "leitor_dedicado": {
        "nome": "Leitor Dedicado",
        "descricao": "Emprestou 5 livros",
        "detalhamento": (
            "Empreste 5 livros diferentes ao longo do tempo. Cada empréstimo conta "
            "uma vez, mesmo que seja do mesmo livro em datas diferentes. Devolva "
            "sempre no prazo pra não travar novos empréstimos."
        ),
        "icone": "📚",
        "categoria": "Biblioteca",
        "raridade": "raro",
        "secreta": False,
        "meta": 5,
        "tipo": "livros",
        "publico": "aluno",
    },
    "rato_de_biblioteca": {
        "nome": "Rato de Biblioteca",
        "descricao": "Emprestou 10 livros",
        "detalhamento": (
            "Continue pegando livros na Biblioteca até somar 10 empréstimos. "
            "Explore gêneros diferentes — o sistema conta qualquer empréstimo, "
            "independente do título."
        ),
        "icone": "🐭",
        "categoria": "Biblioteca",
        "raridade": "epico",
        "secreta": False,
        "meta": 10,
        "tipo": "livros",
        "publico": "aluno",
    },
    "devorador_de_livros": {
        "nome": "Devorador de Livros",
        "descricao": "Emprestou 20 livros",
        "detalhamento": (
            "A conquista mais difícil da Biblioteca. Empreste 20 livros no total. "
            "Como o limite é 1 por vez, é preciso devolver e pegar outro "
            "repetidamente. Vale a pena pelo título de Lendário."
        ),
        "icone": "🔥",
        "categoria": "Biblioteca",
        "raridade": "lendario",
        "secreta": False,
        "meta": 20,
        "tipo": "livros",
        "publico": "aluno",
    },

    # -------- NOTAS --------
    "primeira_nota": {
        "nome": "Primeira Nota",
        "descricao": "Recebeu sua primeira nota",
        "detalhamento": (
            "Assim que um professor lançar qualquer nota no seu boletim, essa "
            "conquista desbloqueia automaticamente. Não precisa fazer nada além "
            "de estar matriculado."
        ),
        "icone": "📝",
        "categoria": "Notas",
        "raridade": "comum",
        "secreta": False,
        "meta": 1,
        "tipo": "notas",
        "publico": "aluno",
    },
    "nota_perfeita": {
        "nome": "Nota Perfeita",
        "descricao": "Tirou 10 em alguma disciplina",
        "detalhamento": (
            "Consiga um 10 em qualquer bimestre de qualquer disciplina. "
            "A conquista é verificada no momento em que o professor lança a nota."
        ),
        "icone": "💯",
        "categoria": "Notas",
        "raridade": "raro",
        "secreta": False,
        "meta": 1,
        "tipo": "nota_dez",
        "publico": "aluno",
    },
    "aprovado": {
        "nome": "Aprovado",
        "descricao": "Média geral maior ou igual a 6",
        "detalhamento": (
            "Tenha as 4 notas de pelo menos uma disciplina lançadas e a média "
            "delas precisa ser >= 6. A média geral considera todas as disciplinas "
            "com 4 notas completas."
        ),
        "icone": "✅",
        "categoria": "Notas",
        "raridade": "comum",
        "secreta": False,
        "meta": 6,
        "tipo": "media",
        "publico": "aluno",
    },
    "aluno_destaque": {
        "nome": "Aluno Destaque",
        "descricao": "Média geral maior ou igual a 9",
        "detalhamento": (
            "Mantenha média geral >= 9 em todas as disciplinas com 4 notas. "
            "Um único 7 já pode derrubar — busque consistência nos 4 bimestres."
        ),
        "icone": "⭐",
        "categoria": "Notas",
        "raridade": "epico",
        "secreta": False,
        "meta": 9,
        "tipo": "media",
        "publico": "aluno",
    },

    # -------- FREQUÊNCIA --------
    "primeira_presenca": {
        "nome": "Primeira Presença",
        "descricao": "Primeira chamada registrada",
        "detalhamento": (
            "Apareça em qualquer chamada feita por um professor. A conquista "
            "desbloqueia independente do status (presente, falta ou justificada)."
        ),
        "icone": "✋",
        "categoria": "Frequência",
        "raridade": "comum",
        "secreta": False,
        "meta": 1,
        "tipo": "presencas",
        "publico": "aluno",
    },
    "frequente": {
        "nome": "Frequente",
        "descricao": "75% ou mais de presença",
        "detalhamento": (
            "Tenha pelo menos 75% de presença em relação ao total de aulas "
            "registradas. Faltas justificadas não contam como presença, mas "
            "também não derrubam tanto quanto faltas comuns."
        ),
        "icone": "📅",
        "categoria": "Frequência",
        "raridade": "raro",
        "secreta": False,
        "meta": 75,
        "tipo": "percentual_presenca",
        "publico": "aluno",
    },
    "presenca_perfeita": {
        "nome": "Presença Perfeita",
        "descricao": "100% de presença",
        "detalhamento": (
            "Compareça a TODAS as aulas registradas. Uma única falta já perde "
            "a conquista permanentemente. Justificadas também contam como "
            "presença quebrada."
        ),
        "icone": "🎯",
        "categoria": "Frequência",
        "raridade": "epico",
        "secreta": False,
        "meta": 100,
        "tipo": "percentual_presenca",
        "publico": "aluno",
    },
    "coruja": {
        "nome": "Coruja",
        "descricao": "Usou o sistema depois das 23h",
        "detalhamento": (
            "Conquista secreta. Basta estar logado no sistema entre 23h e 23h59 "
            "(horário do servidor). A verificação roda quando você abre o "
            "Dashboard ou a página de Conquistas."
        ),
        "icone": "🦉",
        "categoria": "Frequência",
        "raridade": "raro",
        "secreta": True,
        "meta": 1,
        "tipo": "madrugada",
        "publico": "aluno",
    },
    "madrugador": {
        "nome": "Madrugador",
        "descricao": "Usou o sistema antes das 6h",
        "detalhamento": (
            "Conquista secreta. Esteja logado entre 00h e 05h59. Ideal pra "
            "quem estuda de madrugada ou abre o sistema antes de dormir."
        ),
        "icone": "🌅",
        "categoria": "Frequência",
        "raridade": "raro",
        "secreta": True,
        "meta": 1,
        "tipo": "madrugada",
        "publico": "aluno",
    },

    # -------- ESPECIAIS --------
    "rank_top1": {
        "nome": "Melhor da Turma",
        "descricao": "Alcançou o 1º lugar no ranking",
        "detalhamento": (
            "Fique em 1º lugar no Ranking geral. A pontuação soma: média "
            "(até 50 pts), frequência (até 30 pts) e livros emprestados "
            "(até 20 pts). Difícil mas não impossível."
        ),
        "icone": "🥇",
        "categoria": "Especial",
        "raridade": "lendario",
        "secreta": False,
        "meta": 1,
        "tipo": "rank",
        "publico": "aluno",
    },
    "rank_top3": {
        "nome": "Pódio",
        "descricao": "Ficou entre os 3 melhores do ranking",
        "detalhamento": (
            "Entre no Top 3 do Ranking. É bem mais acessível que o 1º lugar "
            "— foque em manter média alta E presença alta simultaneamente."
        ),
        "icone": "🏆",
        "categoria": "Especial",
        "raridade": "epico",
        "secreta": False,
        "meta": 3,
        "tipo": "rank",
        "publico": "aluno",
    },
    "veterano": {
        "nome": "Veterano",
        "descricao": "Mais de 30 dias de cadastro",
        "detalhamento": (
            "Conquista automática. Só de ter conta criada há 30 dias ou mais, "
            "ela desbloqueia na próxima vez que você abrir o Dashboard."
        ),
        "icone": "🎖️",
        "categoria": "Especial",
        "raridade": "raro",
        "secreta": False,
        "meta": 30,
        "tipo": "dias",
        "publico": "aluno",
    },
    "fantasma": {
        "nome": "Fantasma",
        "descricao": "Ficou 30 dias sem logar",
        "detalhamento": (
            "Conquista secreta e irônica: fique 30 dias sem acessar o sistema. "
            "Difícil de conquistar de propósito."
        ),
        "icone": "👻",
        "categoria": "Especial",
        "raridade": "lendario",
        "secreta": True,
        "meta": 30,
        "tipo": "inativo",
        "publico": "aluno",
    },
    "sempre_online": {
        "nome": "Sempre Online",
        "descricao": "Logou 7 dias seguidos",
        "detalhamento": (
            "Conquista secreta. Acesse o sistema por 7 dias consecutivos, "
            "sem faltar nenhum. Um único dia sem login reseta a sequência."
        ),
        "icone": "💻",
        "categoria": "Especial",
        "raridade": "epico",
        "secreta": True,
        "meta": 7,
        "tipo": "sequencia",
        "publico": "aluno",
    },
}


# ============================================
# CONQUISTAS DE PROFESSOR
# ============================================
CONQUISTAS_PROFESSOR = {

    # -------- NOTAS --------
    "primeira_nota_lancada": {
        "nome": "Primeira Nota Lançada",
        "descricao": "Lançou sua primeira nota",
        "detalhamento": (
            "Vá em 'Lançar Nota' no menu, escolha um aluno, disciplina, "
            "bimestre e informe a nota. A primeira que você enviar desbloqueia."
        ),
        "icone": "📝",
        "categoria": "Notas",
        "raridade": "comum",
        "secreta": False,
        "meta": 1,
        "tipo": "notas_lancadas",
        "publico": "professor",
    },
    "professor_atento": {
        "nome": "Professor Atento",
        "descricao": "Lançou 20 notas",
        "detalhamento": (
            "Continue lançando notas até somar 20. Conta qualquer nota em "
            "qualquer disciplina/bimestre dos alunos das suas turmas."
        ),
        "icone": "👀",
        "categoria": "Notas",
        "raridade": "raro",
        "secreta": False,
        "meta": 20,
        "tipo": "notas_lancadas",
        "publico": "professor",
    },
    "mestre_das_notas": {
        "nome": "Mestre das Notas",
        "descricao": "Lançou 100 notas",
        "detalhamento": (
            "Marco de 100 notas. Com turmas grandes, dá pra chegar rápido "
            "lançando em lote por disciplina a cada bimestre."
        ),
        "icone": "📊",
        "categoria": "Notas",
        "raridade": "epico",
        "secreta": False,
        "meta": 100,
        "tipo": "notas_lancadas",
        "publico": "professor",
    },
    "senhor_do_boletim": {
        "nome": "Senhor do Boletim",
        "descricao": "Lançou 500 notas",
        "detalhamento": (
            "A conquista lendária de quem vive lançando nota. 500 notas "
            "corresponde a várias turmas em vários bimestres. Paciência."
        ),
        "icone": "🏅",
        "categoria": "Notas",
        "raridade": "lendario",
        "secreta": False,
        "meta": 500,
        "tipo": "notas_lancadas",
        "publico": "professor",
    },

    # -------- CHAMADAS --------
    "primeira_chamada": {
        "nome": "Primeira Chamada",
        "descricao": "Fez sua primeira chamada",
        "detalhamento": (
            "Vá em Frequência → Fazer Chamada, escolha turma/disciplina/data "
            "e salve. A primeira chamada já desbloqueia."
        ),
        "icone": "✋",
        "categoria": "Frequência",
        "raridade": "comum",
        "secreta": False,
        "meta": 1,
        "tipo": "chamadas_feitas",
        "publico": "professor",
    },
    "professor_presente": {
        "nome": "Professor Presente",
        "descricao": "Fez 10 chamadas",
        "detalhamento": (
            "Registre 10 chamadas no total. Cada chamada salva conta "
            "independente de quantos alunos estavam na turma."
        ),
        "icone": "📋",
        "categoria": "Frequência",
        "raridade": "raro",
        "secreta": False,
        "meta": 10,
        "tipo": "chamadas_feitas",
        "publico": "professor",
    },
    "mestre_da_chamada": {
        "nome": "Mestre da Chamada",
        "descricao": "Fez 50 chamadas",
        "detalhamento": (
            "50 chamadas registradas. Se você dá aula em várias turmas, "
            "uma chamada por aula, isso vira rotina em poucos meses."
        ),
        "icone": "🎓",
        "categoria": "Frequência",
        "raridade": "epico",
        "secreta": False,
        "meta": 50,
        "tipo": "chamadas_feitas",
        "publico": "professor",
    },
    "lenda_da_frequencia": {
        "nome": "Lenda da Frequência",
        "descricao": "Fez 100 chamadas",
        "detalhamento": (
            "Marco lendário: 100 chamadas. Só os professores mais assíduos "
            "chegam lá. Constância absoluta."
        ),
        "icone": "🏆",
        "categoria": "Frequência",
        "raridade": "lendario",
        "secreta": False,
        "meta": 100,
        "tipo": "chamadas_feitas",
        "publico": "professor",
    },

    # -------- TURMAS --------
    "primeira_turma": {
        "nome": "Primeira Turma",
        "descricao": "Tem 1 turma cadastrada",
        "detalhamento": (
            "Peça ao admin para cadastrar pelo menos 1 turma no seu perfil. "
            "Ao editar o professor, informe as turmas separadas por vírgula."
        ),
        "icone": "🏫",
        "categoria": "Turmas",
        "raridade": "comum",
        "secreta": False,
        "meta": 1,
        "tipo": "turmas",
        "publico": "professor",
    },
    "multitarefas": {
        "nome": "Multitarefas",
        "descricao": "Tem 3 turmas cadastradas",
        "detalhamento": (
            "Tenha 3 turmas atribuídas. Basta o admin te cadastrar em mais "
            "turmas no perfil — não precisa dar aula nelas."
        ),
        "icone": "🎯",
        "categoria": "Turmas",
        "raridade": "raro",
        "secreta": False,
        "meta": 3,
        "tipo": "turmas",
        "publico": "professor",
    },
    "super_professor": {
        "nome": "Super Professor",
        "descricao": "Tem 5 turmas cadastradas",
        "detalhamento": (
            "5 turmas no perfil. Professor que atua em várias frentes — "
            "precisa de organização pra dar conta."
        ),
        "icone": "💪",
        "categoria": "Turmas",
        "raridade": "epico",
        "secreta": False,
        "meta": 5,
        "tipo": "turmas",
        "publico": "professor",
    },

    # -------- ESPECIAIS --------
    "primeiro_acesso": {
        "nome": "Bem-vindo",
        "descricao": "Fez o primeiro login",
        "detalhamento": (
            "Conquista automática. Assim que você loga como professor "
            "pela primeira vez, ela desbloqueia."
        ),
        "icone": "👋",
        "categoria": "Especial",
        "raridade": "comum",
        "secreta": False,
        "meta": 1,
        "tipo": "primeiro_login",
        "publico": "professor",
    },
    "professor_veterano": {
        "nome": "Professor Veterano",
        "descricao": "Mais de 60 dias de cadastro",
        "detalhamento": (
            "60 dias desde a criação da sua conta. Pura paciência."
        ),
        "icone": "🎖️",
        "categoria": "Especial",
        "raridade": "raro",
        "secreta": False,
        "meta": 60,
        "tipo": "dias",
        "publico": "professor",
    },
    "professor_lendario": {
        "nome": "Professor Lendário",
        "descricao": "Mais de 180 dias de cadastro",
        "detalhamento": (
            "6 meses de casa. Só os que realmente ficam chegam nessa."
        ),
        "icone": "🌟",
        "categoria": "Especial",
        "raridade": "lendario",
        "secreta": False,
        "meta": 180,
        "tipo": "dias",
        "publico": "professor",
    },
    "coruja_professor": {
        "nome": "Coruja Professor",
        "descricao": "Usou o sistema depois das 23h",
        "detalhamento": (
            "Conquista secreta. Esteja logado entre 23h e 23h59. "
            "Professor que corrige trabalho até tarde."
        ),
        "icone": "🦉",
        "categoria": "Especial",
        "raridade": "raro",
        "secreta": True,
        "meta": 1,
        "tipo": "madrugada",
        "publico": "professor",
    },
    "madrugador_professor": {
        "nome": "Madrugador Professor",
        "descricao": "Usou o sistema antes das 6h",
        "detalhamento": (
            "Conquista secreta. Logado entre 00h e 05h59. "
            "Professor que planeja aula antes do sol nascer."
        ),
        "icone": "🌅",
        "categoria": "Especial",
        "raridade": "raro",
        "secreta": True,
        "meta": 1,
        "tipo": "madrugada",
        "publico": "professor",
    },
    "dedicado": {
        "nome": "Dedicado",
        "descricao": "Fez 10 chamadas E lançou 20 notas",
        "detalhamento": (
            "Conquista secreta. Combine o marco de 10 chamadas com 20 notas "
            "lançadas. Professor que não deixa nada pendente."
        ),
        "icone": "🔥",
        "categoria": "Especial",
        "raridade": "epico",
        "secreta": True,
        "meta": 1,
        "tipo": "dedicado",
        "publico": "professor",
    },
}


# ============================================
# UNIFICADO (usado em buscas por código)
# ============================================
CONQUISTAS = {}
CONQUISTAS.update(CONQUISTAS_ALUNO)
CONQUISTAS.update(CONQUISTAS_PROFESSOR)


RARIDADES = {
    "comum":    {"cor": "#9CA3AF", "label": "Comum",    "brilho": False},
    "raro":     {"cor": "#3B82F6", "label": "Raro",     "brilho": False},
    "epico":    {"cor": "#A855F7", "label": "Épico",    "brilho": True},
    "lendario": {"cor": "#F59E0B", "label": "Lendário", "brilho": True},
}


def get_conquistas_por_publico(publico):
    """Retorna o dicionário de conquistas filtrado por público (aluno/professor)."""
    return {k: v for k, v in CONQUISTAS.items() if v.get("publico") == publico}