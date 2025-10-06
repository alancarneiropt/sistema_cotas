# 🚀 Deploy no Easypanel - Sistema de Cotas

## 📋 **Configuração para Easypanel na Porta 8005**

### **✅ Pré-requisitos:**
- Conta no Easypanel
- Repositório GitHub configurado
- Docker habilitado no Easypanel

---

## 🎯 **Passo a Passo do Deploy:**

### **1. 📥 Preparar o Repositório:**
```bash
# Clone o repositório
git clone https://github.com/alancarneiropt/sistema_cotas.git
cd sistema_cotas

# Execute o script de preparação
python deploy_easypanel.py
```

### **2. 🌐 Configurar no Easypanel:**

#### **A. Criar Novo Projeto:**
1. Acesse o painel do Easypanel
2. Clique em "New Project"
3. Selecione "Git Repository"
4. Cole a URL: `https://github.com/alancarneiropt/sistema_cotas.git`

#### **B. Configurar Porta:**
1. Na seção "Ports"
2. **Porta Interna:** `8000`
3. **Porta Externa:** `8005`
4. **Protocolo:** `HTTP`

#### **C. Configurar Variáveis de Ambiente:**
```env
DEBUG=False
EASYPANEL=True
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=*
DATABASE_URL=sqlite:///db.sqlite3
TIME_ZONE=Europe/Lisbon
LANGUAGE_CODE=pt-br
```

#### **D. Configurar Volumes:**
- **Media:** `/app/media`
- **Logs:** `/app/logs`
- **Static:** `/app/staticfiles`

### **3. 🐳 Configuração Docker:**

#### **Dockerfile Otimizado:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
# ... (já configurado no projeto)
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "sistema_cotas.wsgi:application"]
```

#### **Arquivo easypanel.yml:**
```yaml
version: '3.8'
services:
  sistema-cotas:
    build: .
    ports:
      - "8005:8000"  # Porta externa 8005, interna 8000
    environment:
      - DEBUG=False
      - EASYPANEL=True
    volumes:
      - ./media:/app/media
      - ./logs:/app/logs
```

### **4. 🚀 Executar Deploy:**
1. Clique em "Deploy" no Easypanel
2. Aguarde a construção da imagem
3. Verifique os logs de deploy
4. Acesse: `http://seu-dominio:8005`

---

## ⚙️ **Configurações Específicas:**

### **🔧 Variáveis de Ambiente:**
```env
# Produção
DEBUG=False
EASYPANEL=True
SECRET_KEY=sua-chave-secreta-super-segura
ALLOWED_HOSTS=*

# Banco
DATABASE_URL=sqlite:///db.sqlite3

# Timezone
TIME_ZONE=Europe/Lisbon
LANGUAGE_CODE=pt-br

# Arquivos
STATIC_URL=/static/
MEDIA_URL=/media/
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media
```

### **📁 Volumes Necessários:**
- **Media:** Para upload de imagens e comprovantes
- **Logs:** Para arquivos de log do sistema
- **Static:** Para arquivos estáticos (CSS, JS)

### **🌐 Portas:**
- **Interna:** `8000` (Django/Gunicorn)
- **Externa:** `8005` (Easypanel)
- **Nginx:** `80/443` (opcional)

---

## 🎯 **Funcionalidades Testadas:**

### **✅ Sistema Público:**
- **Landing Page:** `http://seu-dominio:8005/`
- **Fazer Pedido:** Formulário funcional
- **Histórico:** `http://seu-dominio:8005/historico/`
- **Detalhes:** `http://seu-dominio:8005/pedido/{id}/detalhes/`

### **✅ Sistema Administrativo:**
- **Login:** `http://seu-dominio:8005/login/`
- **Dashboard:** `http://seu-dominio:8005/dashboard/`
- **Produtos:** `http://seu-dominio:8005/produtos/`
- **Pedidos:** `http://seu-dominio:8005/admin-pedidos/`

### **✅ Credenciais Padrão:**
- **Usuário:** `admin`
- **Senha:** `admin123`
- **Email:** `admin@sistema-cotas.com`

---

## 🔍 **Verificações Pós-Deploy:**

### **1. 🏠 Teste da Landing Page:**
```bash
curl -I http://seu-dominio:8005/
# Deve retornar: HTTP/1.1 200 OK
```

### **2. 🔐 Teste do Login:**
```bash
curl -I http://seu-dominio:8005/login/
# Deve retornar: HTTP/1.1 200 OK
```

### **3. 📊 Teste do Dashboard:**
```bash
# Após login, acesse:
http://seu-dominio:8005/dashboard/
```

### **4. 🖼️ Teste de Imagens:**
```bash
# Verifique se as imagens carregam:
http://seu-dominio:8005/media/products/imagem.jpg
```

---

## 🛠️ **Troubleshooting:**

### **❌ Problema: Porta não acessível**
**Solução:**
1. Verifique se a porta 8005 está configurada
2. Confirme o mapeamento 8005:8000
3. Reinicie o container

### **❌ Problema: Imagens não carregam**
**Solução:**
1. Verifique o volume `/app/media`
2. Confirme permissões do diretório
3. Reinicie o container

### **❌ Problema: Banco de dados**
**Solução:**
1. Execute migrações: `python manage.py migrate`
2. Crie superusuário: `python manage.py createsuperuser`
3. Verifique logs do container

### **❌ Problema: Arquivos estáticos**
**Solução:**
1. Execute: `python manage.py collectstatic`
2. Verifique volume `/app/staticfiles`
3. Confirme configuração do Nginx

---

## 📞 **Suporte:**

### **🔗 Links Úteis:**
- **Repositório:** https://github.com/alancarneiropt/sistema_cotas.git
- **Documentação:** `README.md`
- **Issues:** https://github.com/alancarneiropt/sistema_cotas/issues

### **📋 Checklist Final:**
- [ ] Repositório configurado
- [ ] Porta 8005 configurada
- [ ] Variáveis de ambiente definidas
- [ ] Volumes configurados
- [ ] Deploy executado
- [ ] Landing page acessível
- [ ] Login funcionando
- [ ] Dashboard carregando
- [ ] Imagens aparecendo
- [ ] Sistema totalmente funcional

---

## 🎉 **Sistema Pronto para Produção!**

### **✅ Status:**
- **Deploy:** Configurado para Easypanel
- **Porta:** 8005
- **Ambiente:** Produção
- **Banco:** SQLite (persistente)
- **Arquivos:** Volumes configurados
- **Segurança:** Configurações de produção aplicadas

### **🚀 Acesso:**
- **Público:** `http://seu-dominio:8005/`
- **Admin:** `http://seu-dominio:8005/login/`
- **Dashboard:** `http://seu-dominio:8005/dashboard/`

**Sistema de Cotas rodando perfeitamente no Easypanel!** 🎯✨
