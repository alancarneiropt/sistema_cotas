#!/bin/bash

# Script de inicialização para o container
echo "🚀 Iniciando Sistema de Cotas..."

# Aguardar um pouco para garantir que tudo está pronto
sleep 3

# Verificar se Django está funcionando
echo "🔍 Verificando Django..."
python manage.py check

# Executar migrações
echo "🗄️ Executando migrações..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Criar superusuário se não existir
echo "👤 Verificando superusuário..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@sistema-cotas.com', 'admin123')
    print('✅ Superusuário criado!')
else:
    print('✅ Superusuário já existe!')
"

# Verificar se tudo está funcionando
echo "🔍 Verificação final..."
python manage.py check

# Executar o servidor
echo "🌐 Iniciando servidor na porta 8000..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile - sistema_cotas.wsgi:application
