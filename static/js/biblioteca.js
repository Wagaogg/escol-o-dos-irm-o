document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById('modalEmprestar');
    if (modal) {
        modal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const livroId = button.getAttribute('data-livro-id');
            const titulo = button.getAttribute('data-titulo');
            
            document.getElementById('livroTitulo').textContent = titulo;
            document.getElementById('livroIdInput').value = livroId;
            
            const tipoUsuario = document.getElementById('tipoUsuario').value;
            const nomeAluno = document.getElementById('nomeAluno').value;
            const inputNome = document.getElementById('nomeAlunoInput');
            
            if (tipoUsuario === 'aluno' && nomeAluno) {
                inputNome.value = nomeAluno;
                inputNome.readOnly = true;
                document.getElementById('helperText').textContent = 'Você só pode emprestar para você mesmo.';
            } else {
                inputNome.value = '';
                inputNome.readOnly = false;
                document.getElementById('helperText').textContent = 'Digite o nome do aluno.';
            }
        });
    }
});