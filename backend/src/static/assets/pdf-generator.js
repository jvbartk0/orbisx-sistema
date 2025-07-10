// Script para interceptar o download de orçamentos e gerar PDF
(function() {
    // Função para gerar PDF do orçamento
    async function gerarPDFOrcamento(orcamentoId) {
        try {
            const response = await fetch(`/api/orcamentos/${orcamentoId}/pdf`, {
                method: 'GET',
                credentials: 'include'
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `orcamento-n${orcamentoId}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                console.error('Erro ao gerar PDF:', response.statusText);
                alert('Erro ao gerar PDF do orçamento');
            }
        } catch (error) {
            console.error('Erro ao gerar PDF:', error);
            alert('Erro ao gerar PDF do orçamento');
        }
    }
    
    // Interceptar cliques nos botões de download
    function interceptarDownloads() {
        // Aguardar o DOM carregar
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', interceptarDownloads);
            return;
        }
        
        // Usar MutationObserver para detectar quando novos elementos são adicionados
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        interceptarBotoes(node);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Interceptar botões já existentes
        interceptarBotoes(document);
    }
    
    function interceptarBotoes(container) {
        // Procurar por botões de download (ícone de download)
        const botoes = container.querySelectorAll('button[title="Baixar"]');
        
        botoes.forEach(botao => {
            if (!botao.dataset.pdfIntercepted) {
                botao.dataset.pdfIntercepted = 'true';
                
                // Remover event listeners existentes
                const novoBotao = botao.cloneNode(true);
                botao.parentNode.replaceChild(novoBotao, botao);
                
                // Adicionar novo event listener
                novoBotao.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Encontrar o ID do orçamento
                    const card = novoBotao.closest('[data-id]') || novoBotao.closest('.orbisx-card');
                    let orcamentoId = null;
                    
                    if (card && card.dataset.id) {
                        orcamentoId = card.dataset.id;
                    } else {
                        // Tentar extrair ID de outro lugar
                        const textoCard = card ? card.textContent : '';
                        const match = textoCard.match(/Orçamento\s*#?(\d+)/i);
                        if (match) {
                            orcamentoId = match[1];
                        }
                    }
                    
                    if (orcamentoId) {
                        gerarPDFOrcamento(orcamentoId);
                    } else {
                        console.error('ID do orçamento não encontrado');
                        alert('Erro: ID do orçamento não encontrado');
                    }
                });
            }
        });
    }
    
    // Inicializar quando a página carregar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', interceptarDownloads);
    } else {
        interceptarDownloads();
    }
})();

