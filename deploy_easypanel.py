#!/usr/bin/env python3
"""
Script de Deploy para Easypanel - Sistema de Cotas
Configurado para rodar na porta 8005
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {command}")
        print(f"Erro: {e.stderr}")
        return None

def setup_easypanel():
    """Configura o ambiente para Easypanel"""
    print("🚀 Configurando Sistema de Cotas para Easypanel...")
    
    # 1. Copiar arquivo de ambiente
    if os.path.exists("env.easypanel"):
        shutil.copy("env.easypanel", ".env")
        print("✅ Arquivo .env configurado para Easypanel")
    
    # 2. Criar diretórios necessários
    directories = ["logs", "media", "static"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Diretório {directory} criado")
    
    # 3. Configurar permissões
    run_command("chmod +x deploy_easypanel.py")
    
    print("✅ Configuração do Easypanel concluída!")

def build_docker():
    """Constrói a imagem Docker"""
    print("🐳 Construindo imagem Docker...")
    
    # Build da imagem
    result = run_command("docker build -t sistema-cotas:latest .")
    if result:
        print("✅ Imagem Docker construída com sucesso!")
        return True
    return False

def run_migrations():
    """Executa as migrações do banco"""
    print("🗄️ Executando migrações...")
    
    # Executar migrações
    result = run_command("python manage.py makemigrations")
    if result:
        result = run_command("python manage.py migrate")
        if result:
            print("✅ Migrações executadas com sucesso!")
            return True
    return False

def collect_static():
    """Coleta arquivos estáticos"""
    print("📦 Coletando arquivos estáticos...")
    
    result = run_command("python manage.py collectstatic --noinput")
    if result:
        print("✅ Arquivos estáticos coletados!")
        return True
    return False

def create_superuser():
    """Cria um superusuário"""
    print("👤 Criando superusuário...")
    
    # Verificar se já existe superusuário
    result = run_command("python manage.py shell -c \"from django.contrib.auth.models import User; print('Superusuário existe' if User.objects.filter(is_superuser=True).exists() else 'Superusuário não existe')\"")
    
    if result and "não existe" in result:
        print("📝 Criando superusuário padrão...")
        print("   Usuário: admin")
        print("   Email: admin@sistema-cotas.com")
        print("   Senha: admin123")
        
        # Criar superusuário
        create_user_script = """
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@sistema-cotas.com', 'admin123')
    print('Superusuário criado com sucesso!')
else:
    print('Superusuário já existe!')
"""
        
        with open("temp_create_user.py", "w") as f:
            f.write(create_user_script)
        
        result = run_command("python manage.py shell < temp_create_user.py")
        os.remove("temp_create_user.py")
        
        if result:
            print("✅ Superusuário criado com sucesso!")
            return True
    else:
        print("✅ Superusuário já existe!")
        return True
    
    return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 DEPLOY SISTEMA DE COTAS - EASYPANEL")
    print("=" * 60)
    print("📍 Porta: 8005")
    print("🌐 Ambiente: Produção")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("manage.py"):
        print("❌ Erro: Execute este script no diretório raiz do projeto!")
        sys.exit(1)
    
    # Configurar ambiente
    setup_easypanel()
    
    # Executar migrações
    if not run_migrations():
        print("❌ Erro nas migrações!")
        sys.exit(1)
    
    # Coletar arquivos estáticos
    if not collect_static():
        print("❌ Erro ao coletar arquivos estáticos!")
        sys.exit(1)
    
    # Criar superusuário
    if not create_superuser():
        print("❌ Erro ao criar superusuário!")
        sys.exit(1)
    
    print("=" * 60)
    print("✅ DEPLOY CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("🎯 Sistema configurado para Easypanel na porta 8005")
    print("🔗 Acesso: http://seu-dominio:8005")
    print("👤 Login: admin / admin123")
    print("=" * 60)
    print("📋 Próximos passos:")
    print("1. Faça upload dos arquivos para o Easypanel")
    print("2. Configure a porta 8005 no painel")
    print("3. Execute o deploy no Easypanel")
    print("4. Teste todas as funcionalidades")
    print("=" * 60)

if __name__ == "__main__":
    main()
