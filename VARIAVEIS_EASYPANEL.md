# 🔧 Variáveis de Ambiente - Easypanel

## ✅ **Configurações Atuais (Corretas):**

```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=cotas.fixdados.store,www.cotas.fixdados.store,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://cotas.fixdados.store,https://www.cotas.fixdados.store
CORS_ALLOWED_ORIGINS=https://cotas.fixdados.store,https://www.cotas.fixdados.store
STATIC_URL=/static/
MEDIA_URL=/media/
PORT=8005
```

## ❌ **Configurações Faltando (Adicionar):**

```env
# Configuração do Easypanel
EASYPANEL=True

# Banco de dados
DATABASE_URL=sqlite:///app/db.sqlite3

# Configurações de fuso horário e idioma
TIME_ZONE=Europe/Lisbon
LANGUAGE_CODE=pt-br

# Configurações de arquivos
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# Configurações de segurança
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# Configurações de email (opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Configurações de logging
LOGGING_LEVEL=INFO

# Configurações do Gunicorn
GUNICORN_WORKERS=3
GUNICORN_TIMEOUT=120
GUNICORN_BIND=0.0.0.0:8000
```

## 🎯 **Configuração Completa para Easypanel:**

```env
# Configuração do Easypanel
EASYPANEL=True
PORT=8005

# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=cotas.fixdados.store,www.cotas.fixdados.store,localhost,127.0.0.1

# Segurança
CSRF_TRUSTED_ORIGINS=https://cotas.fixdados.store,https://www.cotas.fixdados.store
CORS_ALLOWED_ORIGINS=https://cotas.fixdados.store,https://www.cotas.fixdados.store
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# Banco de dados
DATABASE_URL=sqlite:///app/db.sqlite3

# Arquivos estáticos e media
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/app/media

# Configurações de fuso horário e idioma
TIME_ZONE=Europe/Lisbon
LANGUAGE_CODE=pt-br

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Logging
LOGGING_LEVEL=INFO

# Gunicorn
GUNICORN_WORKERS=3
GUNICORN_TIMEOUT=120
GUNICORN_BIND=0.0.0.0:8000
```

## ⚠️ **Importante:**

### **1. 🔧 EASYPANEL=True:**
Esta variável é **CRÍTICA** porque:
- Ativa configurações específicas do Easypanel no `settings.py`
- Define `ALLOWED_HOSTS=['*']` automaticamente
- Configura o sistema para produção

### **2. 🗄️ DATABASE_URL:**
- **Obrigatória** para o banco SQLite funcionar
- Caminho: `/app/db.sqlite3` (dentro do container)

### **3. 📁 STATIC_ROOT e MEDIA_ROOT:**
- **Obrigatórias** para arquivos estáticos e uploads
- Caminhos: `/app/staticfiles` e `/app/media`

### **4. 🌍 TIME_ZONE e LANGUAGE_CODE:**
- **Importantes** para o sistema funcionar corretamente
- Timezone: `Europe/Lisbon`
- Idioma: `pt-br`

## 🚀 **Próximos Passos:**

1. **Adicionar as variáveis faltando** no Easypanel
2. **Especialmente importante:** `EASYPANEL=True`
3. **Salvar as configurações**
4. **Fazer deploy**
5. **Testar o sistema**

## ✅ **Checklist Final:**

- [ ] EASYPANEL=True adicionado
- [ ] DATABASE_URL configurado
- [ ] STATIC_ROOT e MEDIA_ROOT configurados
- [ ] TIME_ZONE e LANGUAGE_CODE configurados
- [ ] Todas as variáveis salvas
- [ ] Deploy executado
- [ ] Sistema testado
