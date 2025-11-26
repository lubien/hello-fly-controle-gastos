// API Base URL
const API_URL = '/api';

// Estado da aplicação
let state = {
    gastos: [],
    categorias: [],
    resumo: {},
    filtros: {
        mes: new Date().getMonth() + 1,
        ano: new Date().getFullYear()
    }
};

// Elementos DOM
const elements = {
    formGasto: document.getElementById('formGasto'),
    listaGastos: document.getElementById('listaGastos'),
    modalGasto: document.getElementById('modalGasto'),
    totalReceitas: document.getElementById('totalReceitas'),
    totalDespesas: document.getElementById('totalDespesas'),
    saldoTotal: document.getElementById('saldoTotal'),
    qtdTransacoes: document.getElementById('qtdTransacoes'),
    selectCategoria: document.getElementById('categoria_id'),
    selectMes: document.getElementById('filtroMes'),
    selectAno: document.getElementById('filtroAno'),
    chartCategorias: null,
    chartEvolucao: null
};

// Inicialização
document.addEventListener('DOMContentLoaded', async () => {
    await inicializarApp();
});

async function inicializarApp() {
    try {
        // Popular selects de filtro
        popularFiltros();
        
        // Carregar categorias
        await carregarCategorias();
        
        // Carregar dados
        await carregarDados();
        
        // Configurar event listeners
        configurarEventListeners();
        
        // Inicializar gráficos
        await inicializarGraficos();
        
    } catch (error) {
        console.error('Erro ao inicializar:', error);
        mostrarToast('Erro ao carregar dados', 'error');
    }
}

function popularFiltros() {
    const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    // Popular meses
    elements.selectMes.innerHTML = meses.map((mes, i) => 
        `<option value="${i + 1}" ${i + 1 === state.filtros.mes ? 'selected' : ''}>${mes}</option>`
    ).join('');
    
    // Popular anos
    const anoAtual = new Date().getFullYear();
    for (let ano = anoAtual; ano >= anoAtual - 5; ano--) {
        const option = document.createElement('option');
        option.value = ano;
        option.textContent = ano;
        if (ano === state.filtros.ano) option.selected = true;
        elements.selectAno.appendChild(option);
    }
}

function configurarEventListeners() {
    // Formulário de gasto
    elements.formGasto.addEventListener('submit', handleSubmitGasto);
    
    // Filtros
    elements.selectMes.addEventListener('change', handleFiltroChange);
    elements.selectAno.addEventListener('change', handleFiltroChange);
    
    // Fechar modal ao clicar fora
    elements.modalGasto.addEventListener('click', (e) => {
        if (e.target === elements.modalGasto) fecharModal();
    });
    
    // Tabs de tipo
    document.querySelectorAll('.tab[data-tipo]').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab[data-tipo]').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById('tipo').value = tab.dataset.tipo;
        });
    });
}

// === API Calls ===

async function carregarCategorias() {
    try {
        const response = await fetch(`${API_URL}/categorias`);
        const data = await response.json();
        
        if (data.success) {
            state.categorias = data.data;
            popularSelectCategorias();
        }
    } catch (error) {
        console.error('Erro ao carregar categorias:', error);
    }
}

async function carregarDados() {
    await Promise.all([
        carregarGastos(),
        carregarResumo()
    ]);
}

async function carregarGastos() {
    try {
        const { mes, ano } = state.filtros;
        const response = await fetch(`${API_URL}/gastos?mes=${mes}&ano=${ano}`);
        const data = await response.json();
        
        if (data.success) {
            state.gastos = data.data;
            renderizarGastos();
        }
    } catch (error) {
        console.error('Erro ao carregar gastos:', error);
    }
}

async function carregarResumo() {
    try {
        const { mes, ano } = state.filtros;
        const response = await fetch(`${API_URL}/relatorios/resumo-mensal?mes=${mes}&ano=${ano}`);
        const data = await response.json();
        
        if (data.success) {
            state.resumo = data.data;
            atualizarCards();
        }
    } catch (error) {
        console.error('Erro ao carregar resumo:', error);
    }
}

async function criarGasto(gasto) {
    const response = await fetch(`${API_URL}/gastos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(gasto)
    });
    return response.json();
}

async function atualizarGasto(id, gasto) {
    const response = await fetch(`${API_URL}/gastos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(gasto)
    });
    return response.json();
}

async function deletarGasto(id) {
    const response = await fetch(`${API_URL}/gastos/${id}`, {
        method: 'DELETE'
    });
    return response.json();
}

// === Event Handlers ===

async function handleSubmitGasto(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const gasto = {
        descricao: formData.get('descricao'),
        valor: parseFloat(formData.get('valor')),
        data: formData.get('data'),
        categoria_id: formData.get('categoria_id') || null,
        tipo: formData.get('tipo'),
        forma_pagamento: formData.get('forma_pagamento')
    };
    
    const gastoId = formData.get('gasto_id');
    
    try {
        let result;
        if (gastoId) {
            result = await atualizarGasto(gastoId, gasto);
        } else {
            result = await criarGasto(gasto);
        }
        
        if (result.success) {
            mostrarToast(gastoId ? 'Gasto atualizado!' : 'Gasto registrado!', 'success');
            fecharModal();
            await carregarDados();
            await atualizarGraficos();
        } else {
            mostrarToast(result.error, 'error');
        }
    } catch (error) {
        mostrarToast('Erro ao salvar gasto', 'error');
    }
}

async function handleFiltroChange() {
    state.filtros.mes = parseInt(elements.selectMes.value);
    state.filtros.ano = parseInt(elements.selectAno.value);
    await carregarDados();
    await atualizarGraficos();
}

async function handleDeletarGasto(id) {
    if (!confirm('Tem certeza que deseja excluir este gasto?')) return;
    
    try {
        const result = await deletarGasto(id);
        if (result.success) {
            mostrarToast('Gasto excluído!', 'success');
            await carregarDados();
            await atualizarGraficos();
        } else {
            mostrarToast(result.error, 'error');
        }
    } catch (error) {
        mostrarToast('Erro ao excluir gasto', 'error');
    }
}

function handleEditarGasto(gasto) {
    document.getElementById('gasto_id').value = gasto.id;
    document.getElementById('descricao').value = gasto.descricao;
    document.getElementById('valor').value = gasto.valor;
    document.getElementById('data').value = gasto.data;
    document.getElementById('categoria_id').value = gasto.categoria_id || '';
    document.getElementById('tipo').value = gasto.tipo;
    document.getElementById('forma_pagamento').value = gasto.forma_pagamento || '';
    
    // Atualizar tabs
    document.querySelectorAll('.tab[data-tipo]').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tipo === gasto.tipo);
    });
    
    document.querySelector('.modal-header h3').textContent = 'Editar Transação';
    abrirModal();
}

// === Renderização ===

function popularSelectCategorias() {
    elements.selectCategoria.innerHTML = '<option value="">Sem categoria</option>';
    state.categorias.forEach(cat => {
        elements.selectCategoria.innerHTML += `
            <option value="${cat.id}">${cat.icone} ${cat.nome}</option>
        `;
    });
}

function atualizarCards() {
    const { total_receitas, total_despesas, saldo, quantidade_transacoes } = state.resumo;
    
    elements.totalReceitas.textContent = formatarMoeda(total_receitas);
    elements.totalDespesas.textContent = formatarMoeda(total_despesas);
    elements.saldoTotal.textContent = formatarMoeda(saldo);
    elements.qtdTransacoes.textContent = quantidade_transacoes;
    
    // Cor do saldo
    elements.saldoTotal.style.color = saldo >= 0 ? '#10b981' : '#f43f5e';
}

function renderizarGastos() {
    if (state.gastos.length === 0) {
        elements.listaGastos.innerHTML = `
            <div class="empty-state">
                <div class="icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/></svg>
                </div>
                <p>Nenhuma transação encontrada</p>
            </div>
        `;
        return;
    }
    
    elements.listaGastos.innerHTML = state.gastos.map(gasto => {
        const categoria = gasto.categoria || { nome: 'Sem categoria', icone: '●', cor: '#64748b' };
        const tipoClass = gasto.tipo === 'receita' ? 'receita' : 'despesa';
        const sinal = gasto.tipo === 'receita' ? '+' : '-';
        
        return `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-icon" style="background: ${categoria.cor}15; color: ${categoria.cor}">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="${categoria.cor}" stroke="none"><circle cx="12" cy="12" r="6"/></svg>
                    </div>
                    <div class="transaction-details">
                        <h4>${gasto.descricao}</h4>
                        <span>${categoria.nome} · ${gasto.forma_pagamento || 'Não informado'}</span>
                    </div>
                </div>
                <div class="transaction-value">
                    <div class="amount ${tipoClass}">${sinal} ${formatarMoeda(gasto.valor)}</div>
                    <div class="date">${formatarData(gasto.data)}</div>
                </div>
                <div class="transaction-actions">
                    <button class="btn btn-outline btn-sm" onclick='handleEditarGasto(${JSON.stringify(gasto)})' title="Editar">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="handleDeletarGasto(${gasto.id})" title="Excluir">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// === Gráficos ===

async function inicializarGraficos() {
    const ctxCategorias = document.getElementById('chartCategorias');
    const ctxEvolucao = document.getElementById('chartEvolucao');
    
    if (!ctxCategorias || !ctxEvolucao) return;
    
    // Configuração global para tema escuro
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = '#1e3a5f';
    
    // Gráfico de categorias (Pizza)
    elements.chartCategorias = new Chart(ctxCategorias, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [],
                borderColor: '#151f32',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e2e8f0',
                        padding: 15,
                        font: { size: 11 }
                    }
                }
            }
        }
    });
    
    // Gráfico de evolução (Linha)
    elements.chartEvolucao = new Chart(ctxEvolucao, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Receitas',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.08)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Despesas',
                    data: [],
                    borderColor: '#f43f5e',
                    backgroundColor: 'rgba(244, 63, 94, 0.08)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e2e8f0',
                        padding: 15,
                        font: { size: 11 }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#1e3a5f'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                x: {
                    grid: {
                        color: '#1e3a5f'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
    
    await atualizarGraficos();
}

async function atualizarGraficos() {
    if (!elements.chartCategorias || !elements.chartEvolucao) return;
    
    try {
        const { mes, ano } = state.filtros;
        
        // Dados por categoria
        const resCategorias = await fetch(`${API_URL}/relatorios/por-categoria?mes=${mes}&ano=${ano}`);
        const dataCategorias = await resCategorias.json();
        
        if (dataCategorias.success && dataCategorias.data.categorias.length > 0) {
            elements.chartCategorias.data.labels = dataCategorias.data.categorias.map(c => c.categoria_nome);
            elements.chartCategorias.data.datasets[0].data = dataCategorias.data.categorias.map(c => c.total);
            elements.chartCategorias.data.datasets[0].backgroundColor = dataCategorias.data.categorias.map(c => c.cor);
            elements.chartCategorias.update();
        }
        
        // Dados de evolução
        const resEvolucao = await fetch(`${API_URL}/relatorios/evolucao?meses=6`);
        const dataEvolucao = await resEvolucao.json();
        
        if (dataEvolucao.success) {
            elements.chartEvolucao.data.labels = dataEvolucao.data.map(d => d.mes_nome);
            elements.chartEvolucao.data.datasets[0].data = dataEvolucao.data.map(d => d.receitas);
            elements.chartEvolucao.data.datasets[1].data = dataEvolucao.data.map(d => d.despesas);
            elements.chartEvolucao.update();
        }
        
    } catch (error) {
        console.error('Erro ao atualizar gráficos:', error);
    }
}

// === Modal ===

function abrirModal() {
    elements.modalGasto.classList.add('active');
}

function fecharModal() {
    elements.modalGasto.classList.remove('active');
    elements.formGasto.reset();
    document.getElementById('gasto_id').value = '';
    document.getElementById('data').value = new Date().toISOString().split('T')[0];
    document.querySelector('.modal-header h3').textContent = 'Nova Transação';
    
    // Reset tabs
    document.querySelectorAll('.tab[data-tipo]').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tipo === 'despesa');
    });
    document.getElementById('tipo').value = 'despesa';
}

function novaTransacao() {
    fecharModal();
    abrirModal();
}

// === Utilitários ===

function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor || 0);
}

function formatarData(data) {
    return new Date(data + 'T00:00:00').toLocaleDateString('pt-BR');
}

function mostrarToast(mensagem, tipo = 'success') {
    const container = document.querySelector('.toast-container') || criarToastContainer();
    
    const iconeSucesso = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>';
    const iconeErro = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
    
    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;
    toast.innerHTML = `
        <span>${tipo === 'success' ? iconeSucesso : iconeErro}</span>
        <span>${mensagem}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function criarToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Inicializar categorias padrão se necessário
async function seedCategorias() {
    try {
        await fetch(`${API_URL}/categorias/seed`, { method: 'POST' });
        await carregarCategorias();
        mostrarToast('Categorias criadas!', 'success');
    } catch (error) {
        mostrarToast('Erro ao criar categorias', 'error');
    }
}
