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
        sqlite3 \
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
ENV DEBUG=False
ENV EASYPANEL=True

# Copiar script de inicialização
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expõe a porta 8005 (interna e externa)
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8005/ || exit 1

# Comando para produção com script de inicialização
ENTRYPOINT ["/app/entrypoint.sh"]
