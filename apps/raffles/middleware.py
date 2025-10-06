"""
Middleware para redirecionamento de autenticação.
"""
from django.shortcuts import redirect
from django.urls import reverse


class AuthRequiredMiddleware:
    """
    Middleware para redirecionar usuários não autenticados para a página de login.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs que não precisam de autenticação
        public_urls = [
            '/',
            '/login/',
            '/sucesso/',
            '/comprovante/',
            '/pedido/',
            '/produto/',
            '/vencedores/',
            '/historico/',
            '/admin/login/',
            '/admin/logout/',
            '/static/',
            '/media/',
        ]
        
        # URLs da API que não precisam de autenticação
        api_public_urls = [
            '/api/products/active/',
            '/api/products/',
        ]
        
        # Verifica se a URL é pública
        is_public_url = any(request.path.startswith(url) for url in public_urls)
        is_api_public_url = any(request.path.startswith(url) for url in api_public_urls)
        
        # Se for uma URL administrativa e o usuário não estiver autenticado
        if (request.path.startswith('/dashboard/') or 
            request.path.startswith('/produtos/') or 
            request.path.startswith('/pedidos/') or 
            request.path.startswith('/logs/') or 
            request.path.startswith('/acoes/')) and not request.user.is_authenticated:
            return redirect(reverse('raffles:custom_login') + f'?next={request.path}')
        
        response = self.get_response(request)
        return response
