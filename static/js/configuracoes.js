// Aplicar configurações ao carregar qualquer página
(function() {
    fetch('/api/configuracoes')
        .then(res => res.json())
        .then(config => {
            aplicarConfig(config);
        })
        .catch(() => {});
})();

function aplicarConfig(config) {
    const root = document.documentElement;
    
    // Tema
    if (config.tema === 'claro') {
        document.body.classList.add('tema-claro');
    } else {
        document.body.classList.remove('tema-claro');
    }
    
    // Cor de destaque
    if (config.cor_destaque) {
        root.style.setProperty('--primary', config.cor_destaque);
    }
    
    // Densidade
    if (config.densidade === 'compacto') {
        document.body.classList.add('densidade-compacto');
    } else {
        document.body.classList.remove('densidade-compacto');
    }
    
    // Fonte
    if (config.fonte && config.fonte !== 'Inter') {
        document.body.style.fontFamily = `"${config.fonte}", sans-serif`;
    }
    
    // Tamanho da fonte
    if (config.tamanho_fonte) {
        document.body.style.fontSize = config.tamanho_fonte + 'px';
    }
    
    // Sidebar recolhida
    if (config.sidebar_recolhida) {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.classList.add('recolhida');
    }
}