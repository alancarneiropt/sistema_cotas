#!/usr/bin/env python
"""
Script de Deploy para Sistema de Cotas
Execute este script para preparar o sistema para produção
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Configura o Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cotas.settings')
    django.setup()

def run_migrations():
    """Executa as migrações"""
    print("🔄 Executando migrações...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    print("✅ Migrações concluídas!")

def collect_static():
    """Coleta arquivos estáticos"""
    print("📁 Coletando arquivos estáticos...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    print("✅ Arquivos estáticos coletados!")

def create_superuser():
    """Cria superusuário"""
    print("👤 Criando superusuário...")
    from django.contrib.auth.models import User
    
    username = input("Digite o nome de usuário (admin): ").strip() or "admin"
    email = input("Digite o email: ").strip()
    password = input("Digite a senha: ").strip()
    
    if not password:
        print("❌ Senha é obrigatória!")
        return
    
    try:
        user = User.objects.create_superuser(username, email, password)
        print(f"✅ Superusuário '{username}' criado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando deploy do Sistema de Cotas...")
    print("=" * 50)
    
    try:
        setup_django()
        
        # Executar migrações
        run_migrations()
        
        # Coletar arquivos estáticos
        collect_static()
        
        # Criar superusuário
        create_superuser()
        
        print("=" * 50)
        print("🎉 Deploy concluído com sucesso!")
        print("📋 Próximos passos:")
        print("1. Configure o arquivo .env com suas credenciais")
        print("2. Configure o servidor web (nginx/apache)")
        print("3. Configure o banco PostgreSQL")
        print("4. Execute: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Erro durante o deploy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
