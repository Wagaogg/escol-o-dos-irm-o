// Script para adicionar/remover responsáveis no cadastro de aluno
document.addEventListener('DOMContentLoaded', function() {
    const addBtn = document.getElementById('add-responsavel');
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            const container = document.getElementById('responsaveis-container');
            const items = container.querySelectorAll('.responsavel-item');
            const clone = items[0].cloneNode(true);
            clone.querySelectorAll('input').forEach(inp => inp.value = '');
            container.appendChild(clone);
        });
    }

    // Delegação de eventos para remover
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remover-responsavel')) {
            const item = e.target.closest('.responsavel-item');
            const total = document.querySelectorAll('.responsavel-item').length;
            if (total > 1) {
                item.remove();
            } else {
                alert('Deve haver pelo menos um responsável.');
            }
        }
    });
});