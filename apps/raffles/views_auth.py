"""
Views de autenticação para a app raffles.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse


def custom_login(request):
    """
    Tela de login personalizada.
    """
    if request.user.is_authenticated:
        return redirect(reverse('raffles:admin_dashboard'))
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    messages.success(request, f'Bem-vindo(a), {user.first_name or user.username}!')
                    return redirect(reverse('raffles:admin_dashboard'))
                else:
                    messages.error(request, 'Acesso negado. Apenas administradores podem acessar este sistema.')
            else:
                messages.error(request, 'Usuário ou senha incorretos.')
        else:
            messages.error(request, 'Por favor, preencha todos os campos.')
    
    return render(request, 'raffles/login.html')


def custom_logout(request):
    """
    Logout personalizado.
    """
    logout(request)
    messages.info(request, 'Você foi desconectado com sucesso.')
    return redirect(reverse('raffles:custom_login'))


@login_required
def profile(request):
    """
    Página de perfil do usuário.
    """
    return render(request, 'raffles/profile.html', {
        'user': request.user
    })
