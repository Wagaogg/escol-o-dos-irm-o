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
    const body = document.body;
    
    // =========================
    // TEMA
    // =========================
    if (config.tema === 'claro') {
        body.classList.add('tema-claro');
        body.classList.remove('tema-escuro');
    } else {
        body.classList.add('tema-escuro');
        body.classList.remove('tema-claro');
    }
    
    // =========================
    // COR DE DESTAQUE
    // =========================
    if (config.cor_destaque) {
        // Guarda localmente para a próxima página já nascer com a cor correta.
        try { localStorage.setItem('seapp_cor_destaque', config.cor_destaque); } catch (e) {}

        root.style.setProperty('--primary', config.cor_destaque);
        
        const hover = escurecerCor(config.cor_destaque, 0.15);
        root.style.setProperty('--primary-hover', hover);
        
        // Sobrescrever variáveis do Bootstrap também
        root.style.setProperty('--bs-primary', config.cor_destaque);
        root.style.setProperty('--bs-primary-rgb', hexParaRgb(config.cor_destaque));
        root.style.setProperty('--bs-link-color', config.cor_destaque);
        root.style.setProperty('--bs-link-hover-color', hover);
        root.style.setProperty('--bs-link-color-rgb', hexParaRgb(config.cor_destaque));
    }
    
    // =========================
    // DENSIDADE
    // =========================
    if (config.densidade === 'compacto') {
        body.classList.add('densidade-compacto');
    } else {
        body.classList.remove('densidade-compacto');
    }
    
    // =========================
    // FONTE
    // =========================
    if (config.fonte && config.fonte !== 'Inter') {
        body.style.fontFamily = `"${config.fonte}", sans-serif`;
    } else {
        body.style.fontFamily = '';
    }
    
    // =========================
    // TAMANHO DA FONTE
    // =========================
    if (config.tamanho_fonte) {
        body.style.fontSize = config.tamanho_fonte + 'px';
    }
    
    // =========================
    // SIDEBAR RECOLHIDA
    // =========================
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        if (config.sidebar_recolhida) {
            sidebar.classList.add('recolhida');
        } else {
            sidebar.classList.remove('recolhida');
        }
    }
}

// Função auxiliar: escurecer cor HEX
function escurecerCor(hex, fator) {
    hex = hex.replace('#', '');
    
    let r = parseInt(hex.substring(0, 2), 16);
    let g = parseInt(hex.substring(2, 4), 16);
    let b = parseInt(hex.substring(4, 6), 16);
    
    r = Math.max(0, Math.floor(r * (1 - fator)));
    g = Math.max(0, Math.floor(g * (1 - fator)));
    b = Math.max(0, Math.floor(b * (1 - fator)));
    
    const paraHex = (n) => n.toString(16).padStart(2, '0');
    
    return '#' + paraHex(r) + paraHex(g) + paraHex(b);
}

// Função auxiliar: HEX → RGB
function hexParaRgb(hex) {
    hex = hex.replace('#', '');
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    return `${r}, ${g}, ${b}`;
}