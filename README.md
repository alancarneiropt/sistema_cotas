# Sistema de Cotas/Sorteios em Django

Sistema web completo para venda de cotas de sorteios por produto, com alocação aleatória de números, gerenciamento de pedidos e dashboard administrativo.
teste
## 🚀 Características

- **Venda de cotas por produto**: Cada produto tem um número específico de cotas
- **Alocação aleatória**: O sistema escolhe automaticamente os números das cotas
- **Gestão de pedidos**: Reserva, confirmação e controle de status
- **Dashboard administrativo**: Interface completa para gerenciamento
- **Sistema de sorteios**: Realização e registro de sorteios
- **Interface responsiva**: Design moderno com Bootstrap 5
- **API REST**: Endpoints para integração (opcional)

## 🛠️ Tecnologias

- **Backend**: Django 5.x
- **Banco de Dados**: PostgreSQL (configurável para SQLite em desenvolvimento)
- **Frontend**: Bootstrap 5, JavaScript vanilla
- **Uploads**: Sistema de arquivos local (configurável para S3)
- **Timezone**: Europe/Lisbon (configurável)
- **Moeda**: BRL (R$)

## 📋 Pré-requisitos

- Python 3.11+
- PostgreSQL (opcional, pode usar SQLite)
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd Sistema_Cotas
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `env.example` para `.env` e configure as variáveis:

```bash
cp env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sistema_cotas

# Django Settings
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### 5. Configure o banco de dados

#### Opção A: SQLite (desenvolvimento)
O sistema já está configurado para usar SQLite por padrão.

#### Opção B: PostgreSQL (produção)
1. Instale o PostgreSQL
2. Crie um banco de dados
3. Atualize as configurações no `.env`

### 6. Execute as migrations

```bash
python manage.py migrate
```

### 7. Crie dados de exemplo (opcional)

```bash
python create_superuser.py
```

Este script criará:
- Superusuário (admin/admin123)
- 3 produtos de exemplo
- Cotas para cada produto
- Pedidos de exemplo

### 8. Inicie o servidor

```bash
python manage.py runserver
```

O sistema estará disponível em: http://localhost:8000

## 📱 Uso do Sistema

### Acesso Público

- **Home**: `http://localhost:8000/`
- **Vencedores**: `http://localhost:8000/vencedores/`

### Área Administrativa

- **Django Admin**: `http://localhost:8000/admin/`
- **Dashboard Customizado**: `http://localhost:8000/admin/dashboard/`

**Credenciais padrão:**
- Usuário: `admin`
- Senha: `admin123`

## 🎯 Funcionalidades

### Para Clientes

1. **Visualizar Produtos**: Lista de sorteios ativos com informações detalhadas
2. **Comprar Cotas**: Formulário para adquirir cotas (números sorteados automaticamente)
3. **Enviar Comprovante**: Upload de comprovante de pagamento
4. **Acompanhar Pedido**: Consulta do status do pedido
5. **Ver Vencedores**: Lista de sorteios realizados

### Para Administradores

1. **Gerenciar Produtos**: Criar, editar e controlar produtos/sorteios
2. **Dashboard**: Visão geral com estatísticas em tempo real
3. **Gerenciar Pedidos**: Confirmar, cancelar e acompanhar pedidos
4. **Realizar Sorteios**: Executar sorteios e definir vencedores
5. **Logs**: Histórico de ações administrativas

## 🔧 Comandos de Gerenciamento

### Liberar Reservas Expiradas

```bash
python manage.py release_expired_reservations
```

### Criar Cotas para Produtos

```bash
python manage.py create_quotas --all
python manage.py create_quotas 1 2 3  # IDs específicos
```

### Modo Simulação

```bash
python manage.py release_expired_reservations --dry-run
python manage.py create_quotas --all --dry-run
```

## ⚙️ Configurações Avançadas

### Agendamento de Tarefas

#### Opção 1: Django Crontab

```bash
pip install django-crontab
python manage.py crontab add
```

#### Opção 2: Celery (Recomendado para produção)

```bash
pip install celery redis

# Terminal 1 - Worker
celery -A sistema_cotas worker --loglevel=info

# Terminal 2 - Beat (agendador)
celery -A sistema_cotas beat --loglevel=info
```

### Configuração de E-mail

Para produção, configure um serviço de e-mail real:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### Upload para S3 (Opcional)

```bash
pip install boto3 django-storages
```

Configure no `settings.py`:

```python
# AWS S3 Configuration
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = 'sua-chave'
AWS_SECRET_ACCESS_KEY = 'sua-chave-secreta'
AWS_STORAGE_BUCKET_NAME = 'seu-bucket'
```

## 📊 Estrutura do Projeto

```
Sistema_Cotas/
├── manage.py
├── requirements.txt
├── create_superuser.py
├── sistema_cotas/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
├── apps/
│   └── raffles/
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py
│       ├── views.py
│       ├── views_admin.py
│       ├── forms.py
│       ├── admin.py
│       ├── services.py
│       ├── signals.py
│       ├── tasks.py
│       ├── urls.py
│       ├── api_urls.py
│       └── management/
│           └── commands/
│               ├── release_expired_reservations.py
│               └── create_quotas.py
├── templates/
│   ├── base.html
│   └── raffles/
│       ├── public_home.html
│       ├── order_success.html
│       ├── admin_dashboard.html
│       └── ...
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── media/
    ├── products/
    └── receipts/
```

## 🗄️ Modelos de Dados

### Product
- Título, descrição, preço por cota
- Total de cotas, status (rascunho/ativo/encerrado)
- Data do sorteio, número sorteado

### Order
- Dados do cliente (nome, e-mail, WhatsApp)
- Quantidade de cotas, valor total
- Status (reservado/confirmado/cancelado/expirado)
- Comprovante de pagamento

### Quota
- Número da cota (1 até total_quotas)
- Status (disponível/reservada/vendida)
- Pedido associado

### AdminLog
- Log de ações administrativas
- Detalhes em JSON

## 🔒 Segurança

- **CSRF Protection**: Habilitado por padrão
- **Rate Limiting**: Configurado na API
- **Validação de Upload**: Tipos e tamanhos de arquivo
- **Sanitização**: Dados de entrada validados
- **Logs de Auditoria**: Todas as ações administrativas registradas

## 🧪 Testes

Para executar os testes (quando implementados):

```bash
python manage.py test
```

## 🚀 Deploy em Produção

### 🎯 Easypanel (Recomendado)
```bash
# Configurar para Easypanel na porta 8005
python deploy_easypanel.py

# Seguir guia: DEPLOY_EASYPANEL.md
```

### Configurações de Segurança

1. **SECRET_KEY**: Use uma chave secreta forte
2. **DEBUG**: Defina como `False`
3. **ALLOWED_HOSTS**: Configure os domínios permitidos
4. **HTTPS**: Configure SSL/TLS
5. **Database**: Use PostgreSQL em produção

### Variáveis de Ambiente de Produção

```env
DEBUG=False
SECRET_KEY=chave-secreta-muito-forte
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
DATABASE_URL=postgresql://user:password@localhost:5432/sistema_cotas
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

### Comandos de Deploy

```bash
# Coletar arquivos estáticos
python manage.py collectstatic

# Executar migrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para suporte e dúvidas:

- **Issues**: Abra uma issue no GitHub
- **Documentação**: Consulte este README
- **E-mail**: contato@sistemacotas.com

## 📈 Roadmap

- [ ] Sistema de notificações por e-mail
- [ ] Integração com gateway de pagamento
- [ ] App mobile (React Native)
- [ ] Sistema de afiliados
- [ ] Relatórios avançados
- [ ] API completa com autenticação JWT
- [ ] Sistema de chat em tempo real
- [ ] Integração com redes sociais

## 🎉 Agradecimentos

- Django Framework
- Bootstrap
- Comunidade Python/Django
- Contribuidores do projeto

---

**Desenvolvido com ❤️ para facilitar a gestão de sorteios e cotas**
