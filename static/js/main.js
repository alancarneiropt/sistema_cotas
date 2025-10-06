/**
 * JavaScript principal para o Sistema de Cotas
 */

// Configurações globais
const SistemaCotas = {
    config: {
        apiBaseUrl: '/api/',
        refreshInterval: 30000, // 30 segundos
        countdownInterval: 1000, // 1 segundo
    },
    
    // Inicialização
    init: function() {
        this.setupEventListeners();
        this.setupCountdowns();
        this.setupAutoRefresh();
        this.setupFormValidation();
        this.setupTooltips();
    },
    
    // Event listeners
    setupEventListeners: function() {
        // Formulários com loading state
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });
        
        // Botões de ação
        document.querySelectorAll('[data-action]').forEach(button => {
            button.addEventListener('click', this.handleAction.bind(this));
        });
        
        // Atualização de preços em tempo real
        document.querySelectorAll('#id_product, #id_quantity').forEach(input => {
            input.addEventListener('change', this.updateTotalPrice.bind(this));
        });
        
        // Fechar alertas automaticamente
        document.querySelectorAll('.alert').forEach(alert => {
            setTimeout(() => {
                this.fadeOut(alert);
            }, 5000);
        });
    },
    
    // Manipulação de formulários
    handleFormSubmit: function(event) {
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner"></span> Processando...';
            submitBtn.disabled = true;
            
            // Reabilita o botão após 10 segundos (fallback)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 10000);
        }
    },
    
    // Atualização de preço total
    updateTotalPrice: function() {
        const productSelect = document.getElementById('id_product');
        const quantityInput = document.getElementById('id_quantity');
        const totalDisplay = document.getElementById('totalDisplay');
        const totalAmount = document.getElementById('totalAmount');
        
        if (!productSelect || !quantityInput || !totalDisplay || !totalAmount) {
            return;
        }
        
        const selectedOption = productSelect.options[productSelect.selectedIndex];
        const priceCents = parseInt(selectedOption?.dataset.price || 0);
        const quantity = parseInt(quantityInput.value) || 0;
        
        if (priceCents > 0 && quantity > 0) {
            const totalCents = priceCents * quantity;
            const totalReais = (totalCents / 100).toFixed(2).replace('.', ',');
            totalAmount.textContent = 'R$ ' + totalReais;
            totalDisplay.style.display = 'block';
        } else {
            totalDisplay.style.display = 'none';
        }
    },
    
    // Countdown timers
    setupCountdowns: function() {
        document.querySelectorAll('[data-countdown]').forEach(element => {
            const endTime = new Date(element.dataset.countdown).getTime();
            this.startCountdown(element, endTime);
        });
    },
    
    startCountdown: function(element, endTime) {
        const updateCountdown = () => {
            const now = new Date().getTime();
            const timeLeft = endTime - now;
            
            if (timeLeft > 0) {
                const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
                const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
                
                element.innerHTML = `
                    ${days > 0 ? days + 'd ' : ''}
                    ${hours.toString().padStart(2, '0')}:
                    ${minutes.toString().padStart(2, '0')}:
                    ${seconds.toString().padStart(2, '0')}
                `;
            } else {
                element.innerHTML = 'Expirado';
                element.style.color = '#dc3545';
                clearInterval(this.countdownInterval);
            }
        };
        
        updateCountdown();
        this.countdownInterval = setInterval(updateCountdown, 1000);
    },
    
    // Auto-refresh para dados em tempo real
    setupAutoRefresh: function() {
        if (window.location.pathname.includes('admin')) {
            setInterval(() => {
                this.refreshStats();
            }, this.config.refreshInterval);
        }
    },
    
    refreshStats: function() {
        fetch(this.config.apiBaseUrl + 'stats/')
            .then(response => response.json())
            .then(data => {
                this.updateStatsDisplay(data);
            })
            .catch(error => {
                console.log('Erro ao atualizar estatísticas:', error);
            });
    },
    
    updateStatsDisplay: function(data) {
        // Atualiza elementos com data-stat
        Object.keys(data).forEach(key => {
            const elements = document.querySelectorAll(`[data-stat="${key}"]`);
            elements.forEach(element => {
                element.textContent = data[key];
            });
        });
    },
    
    // Validação de formulários
    setupFormValidation: function() {
        // Validação de WhatsApp
        document.querySelectorAll('input[name="whatsapp"]').forEach(input => {
            input.addEventListener('blur', this.validateWhatsApp.bind(this));
        });
        
        // Validação de quantidade
        document.querySelectorAll('input[name="quantity"]').forEach(input => {
            input.addEventListener('input', this.validateQuantity.bind(this));
        });
    },
    
    validateWhatsApp: function(event) {
        const input = event.target;
        const value = input.value.trim().replace(/\D/g, '');
        
        if (value && !value.startsWith('55')) {
            input.value = '+55' + value;
        }
    },
    
    validateQuantity: function(event) {
        const input = event.target;
        const value = parseInt(input.value) || 0;
        const maxQuotas = parseInt(input.dataset.maxQuotas || 100);
        
        if (value > maxQuotas) {
            input.value = maxQuotas;
            this.showToast('Quantidade máxima permitida: ' + maxQuotas, 'warning');
        }
        
        if (value < 1) {
            input.value = 1;
        }
    },
    
    // Tooltips
    setupTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },
    
    // Ações de botões
    handleAction: function(event) {
        const button = event.target.closest('[data-action]');
        const action = button.dataset.action;
        const id = button.dataset.id;
        
        switch (action) {
            case 'select-product':
                this.selectProduct(id);
                break;
            case 'confirm-order':
                this.confirmOrder(id);
                break;
            case 'cancel-order':
                this.cancelOrder(id);
                break;
            case 'draw-product':
                this.drawProduct(id);
                break;
            default:
                console.log('Ação não reconhecida:', action);
        }
    },
    
    selectProduct: function(productId) {
        const productSelect = document.getElementById('id_product');
        if (productSelect) {
            productSelect.value = productId;
            this.updateTotalPrice();
            document.getElementById('orderForm')?.scrollIntoView({ behavior: 'smooth' });
        }
    },
    
    confirmOrder: function(orderId) {
        if (confirm('Confirmar este pedido?')) {
            this.performAction('confirm-order', orderId);
        }
    },
    
    cancelOrder: function(orderId) {
        if (confirm('Cancelar este pedido?')) {
            this.performAction('cancel-order', orderId);
        }
    },
    
    drawProduct: function(productId) {
        if (confirm('Realizar sorteio para este produto?')) {
            this.performAction('draw-product', productId);
        }
    },
    
    performAction: function(action, id) {
        const url = `/admin/actions/${action}/${id}/`;
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showToast(data.message || 'Ação realizada com sucesso!', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                this.showToast(data.error || 'Erro ao realizar ação', 'danger');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            this.showToast('Erro interno. Tente novamente.', 'danger');
        });
    },
    
    // Utilitários
    getCSRFToken: function() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    },
    
    showToast: function(message, type = 'info') {
        const toastContainer = this.getOrCreateToastContainer();
        const toast = this.createToast(message, type);
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },
    
    getOrCreateToastContainer: function() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        return container;
    },
    
    createToast: function(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        return toast;
    },
    
    fadeOut: function(element) {
        element.style.transition = 'opacity 0.5s';
        element.style.opacity = '0';
        setTimeout(() => {
            element.remove();
        }, 500);
    },
    
    // Animações
    animateNumber: function(element, start, end, duration = 1000) {
        const startTime = performance.now();
        
        const updateNumber = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (end - start) * progress);
            element.textContent = current.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        
        requestAnimationFrame(updateNumber);
    },
    
    // Animações de entrada
    animateOnScroll: function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        });
        
        elements.forEach(element => {
            observer.observe(element);
        });
    }
};

// Funções auxiliares globais
function selectProduct(productId) {
    SistemaCotas.selectProduct(productId);
}

function confirmOrder(orderId) {
    SistemaCotas.confirmOrder(orderId);
}

function cancelOrder(orderId) {
    SistemaCotas.cancelOrder(orderId);
}

function drawProduct(productId) {
    SistemaCotas.drawProduct(productId);
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    SistemaCotas.init();
    
    // Adiciona classe para animações
    document.body.classList.add('fade-in');
    
    // Configura animações on scroll
    SistemaCotas.animateOnScroll();
    
    // Atualiza preço total se houver valores iniciais
    SistemaCotas.updateTotalPrice();
});

// Tratamento de erros globais
window.addEventListener('error', function(event) {
    console.error('Erro JavaScript:', event.error);
});

// Tratamento de erros de fetch
window.addEventListener('unhandledrejection', function(event) {
    console.error('Erro de Promise:', event.reason);
});

// Exporta para uso em outros scripts
window.SistemaCotas = SistemaCotas;
