# 🚀 Guia de Deploy - Sistema de Cotas

## 📋 **Pré-requisitos**

### **🖥️ Servidor:**
- Ubuntu 20.04+ ou similar
- Python 3.11+
- PostgreSQL 13+
- Nginx
- SSL Certificate (Let's Encrypt)

### **📦 Dependências:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip postgresql nginx certbot python3-certbot-nginx
```

## 🔧 **Configuração do Ambiente**

### **1. 📁 Preparar Diretório:**
```bash
sudo mkdir -p /var/www/sistema-cotas
sudo chown -R $USER:$USER /var/www/sistema-cotas
cd /var/www/sistema-cotas
```

### **2. 🐍 Configurar Python:**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### **3. 📦 Instalar Dependências:**
```bash
pip install -r requirements.production.txt
```

## 🗄️ **Configuração do Banco de Dados**

### **1. 🐘 Configurar PostgreSQL:**
```bash
sudo -u postgres psql
```

### **2. 📊 Criar Banco e Usuário:**
```sql
CREATE DATABASE sistema_cotas;
CREATE USER sistema_user WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE sistema_cotas TO sistema_user;
\q
```

### **3. 🔧 Configurar .env:**
```bash
cp env.production .env
nano .env
```

**Configurações importantes:**
```env
DEBUG=False
SECRET_KEY=sua-chave-secreta-muito-longa-e-segura
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
DATABASE_URL=postgresql://sistema_user:sua_senha_segura@localhost:5432/sistema_cotas
```

## 🚀 **Deploy da Aplicação**

### **1. 📁 Copiar Arquivos:**
```bash
# Copie todos os arquivos do projeto para /var/www/sistema-cotas/
```

### **2. 🔄 Executar Deploy:**
```bash
python deploy.py
```

### **3. 🧪 Testar Aplicação:**
```bash
python manage.py runserver 0.0.0.0:8000
```

## 🌐 **Configuração do Nginx**

### **1. 📄 Copiar Configuração:**
```bash
sudo cp nginx.conf /etc/nginx/sites-available/sistema-cotas
sudo ln -s /etc/nginx/sites-available/sistema-cotas /etc/nginx/sites-enabled/
```

### **2. 🔧 Editar Configuração:**
```bash
sudo nano /etc/nginx/sites-available/sistema-cotas
```

**Alterar:**
- `seu-dominio.com` → seu domínio real
- `/path/to/your/project/` → `/var/www/sistema-cotas/`
- Caminhos SSL

### **3. ✅ Testar e Recarregar:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 **Configuração SSL**

### **1. 📜 Obter Certificado:**
```bash
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

### **2. 🔄 Renovação Automática:**
```bash
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## ⚙️ **Configuração do Systemd**

### **1. 📄 Copiar Serviço:**
```bash
sudo cp sistema-cotas.service /etc/systemd/system/
```

### **2. 🔧 Editar Serviço:**
```bash
sudo nano /etc/systemd/system/sistema-cotas.service
```

**Alterar:**
- `/path/to/your/project/` → `/var/www/sistema-cotas/`
- `/path/to/your/venv/` → `/var/www/sistema-cotas/venv/`

### **3. 🚀 Ativar Serviço:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable sistema-cotas
sudo systemctl start sistema-cotas
sudo systemctl status sistema-cotas
```

## 📊 **Monitoramento**

### **1. 📈 Logs da Aplicação:**
```bash
sudo journalctl -u sistema-cotas -f
```

### **2. 📊 Logs do Nginx:**
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### **3. 🔍 Status dos Serviços:**
```bash
sudo systemctl status sistema-cotas
sudo systemctl status nginx
sudo systemctl status postgresql
```

## 🔧 **Comandos Úteis**

### **🔄 Reiniciar Aplicação:**
```bash
sudo systemctl restart sistema-cotas
```

### **📁 Coletar Arquivos Estáticos:**
```bash
cd /var/www/sistema-cotas
source venv/bin/activate
python manage.py collectstatic --noinput
```

### **🗄️ Backup do Banco:**
```bash
sudo -u postgres pg_dump sistema_cotas > backup_$(date +%Y%m%d_%H%M%S).sql
```

### **🔄 Restaurar Backup:**
```bash
sudo -u postgres psql sistema_cotas < backup_arquivo.sql
```

## 🛡️ **Segurança**

### **✅ Configurações Aplicadas:**
- **DEBUG=False** em produção
- **SSL/TLS** obrigatório
- **Headers de segurança** no Nginx
- **Firewall** configurado
- **Senhas seguras** para banco
- **Usuário dedicado** para aplicação

### **🔒 Recomendações Adicionais:**
- Configure fail2ban
- Monitore logs de acesso
- Mantenha dependências atualizadas
- Faça backups regulares
- Use senhas fortes

## 🎯 **Verificação Final**

### **✅ Checklist de Deploy:**
- [ ] Aplicação rodando em https://seu-dominio.com
- [ ] SSL funcionando
- [ ] Banco de dados conectado
- [ ] Arquivos estáticos servindo
- [ ] Upload de imagens funcionando
- [ ] Login administrativo funcionando
- [ ] Responsividade em dispositivos móveis

### **🧪 Testes:**
1. **Acesse:** https://seu-dominio.com
2. **Faça login:** admin / sua-senha
3. **Crie um produto** de teste
4. **Faça um pedido** público
5. **Teste** em diferentes dispositivos

## 🆘 **Solução de Problemas**

### **❌ Erro 502 Bad Gateway:**
```bash
sudo systemctl status sistema-cotas
sudo journalctl -u sistema-cotas -f
```

### **❌ Erro de Banco de Dados:**
```bash
sudo systemctl status postgresql
sudo -u postgres psql -l
```

### **❌ Arquivos Estáticos não Carregam:**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### **❌ SSL não Funciona:**
```bash
sudo certbot certificates
sudo nginx -t
```

## 🎉 **Deploy Concluído!**

**Seu Sistema de Cotas está rodando em produção!**

### **📱 URLs Importantes:**
- **Site Público:** https://seu-dominio.com
- **Admin:** https://seu-dominio.com/login/
- **Dashboard:** https://seu-dominio.com/dashboard/

### **📞 Suporte:**
- **Logs:** `sudo journalctl -u sistema-cotas -f`
- **Status:** `sudo systemctl status sistema-cotas`
- **Reiniciar:** `sudo systemctl restart sistema-cotas`

**Sistema pronto para uso em produção!** 🚀✨
