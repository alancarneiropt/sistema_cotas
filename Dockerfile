FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p logs media staticfiles

# Configura variáveis de ambiente
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=sistema_cotas.settings

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expõe a porta 8000 (interna) - Easypanel mapeará para 8005
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Comando para produção com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "sistema_cotas.wsgi:application"]
