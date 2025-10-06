# ✅ Checklist de Deploy - Sistema de Cotas

## 🎯 **Configuração para Easypanel - Porta 8005**

### **📋 Pré-Deploy:**

#### **✅ Arquivos Verificados:**
- [ ] `Dockerfile` - Configurado com Gunicorn e WhiteNoise
- [ ] `entrypoint.sh` - Script de inicialização funcional
- [ ] `requirements.txt` - Todas as dependências incluídas
- [ ] `sistema_cotas/settings.py` - Configurado para Easypanel
- [ ] `easypanel.yml` - Configuração Docker Compose
- [ ] `.gitignore` - Arquivos desnecessários ignorados

#### **✅ Dependências:**
- [ ] Django 5.x
- [ ] Gunicorn (servidor WSGI)
- [ ] WhiteNoise (arquivos estáticos)
- [ ] Pillow (imagens)
- [ ] psycopg (PostgreSQL - opcional)
- [ ] python-dotenv (variáveis de ambiente)

### **🐳 Configuração Docker:**

#### **✅ Dockerfile:**
- [ ] Base Python 3.11-slim
- [ ] Dependências do sistema instaladas
- [ ] Diretórios criados (logs, media, staticfiles)
- [ ] Script de inicialização configurado
- [ ] Porta 8000 exposta
- [ ] Health check configurado

#### **✅ Script de Inicialização:**
- [ ] Verificação do Django
- [ ] Migrações automáticas
- [ ] Coleta de arquivos estáticos
- [ ] Criação de superusuário
- [ ] Inicialização do Gunicorn

### **⚙️ Configurações Django:**

#### **✅ Settings.py:**
- [ ] DEBUG=False para produção
- [ ] ALLOWED_HOSTS=['*'] para Easypanel
- [ ] WhiteNoise configurado
- [ ] Banco SQLite configurado
- [ ] Timezone Europe/Lisbon
- [ ] Idioma pt-br

### **🌐 Configuração Easypanel:**

#### **✅ Variáveis de Ambiente:**
```env
DEBUG=False
EASYPANEL=True
SECRET_KEY=sua-chave-secreta
DATABASE_URL=sqlite:///app/db.sqlite3
TIME_ZONE=Europe/Lisbon
LANGUAGE_CODE=pt-br
ALLOWED_HOSTS=*
```

#### **✅ Portas:**
- [ ] Porta Externa: 8005
- [ ] Porta Interna: 8000
- [ ] Protocolo: HTTP

#### **✅ Volumes:**
- [ ] media_data:/app/media
- [ ] logs_data:/app/logs
- [ ] static_data:/app/staticfiles

### **🚀 Deploy:**

#### **✅ Passos do Deploy:**
1. [ ] Conectar repositório GitHub
2. [ ] Configurar porta 8005
3. [ ] Definir variáveis de ambiente
4. [ ] Configurar volumes
5. [ ] Executar deploy
6. [ ] Verificar logs
7. [ ] Testar aplicação

### **🧪 Testes Pós-Deploy:**

#### **✅ Funcionalidades Básicas:**
- [ ] Landing page acessível: `http://dominio:8005/`
- [ ] Login funcionando: `http://dominio:8005/login/`
- [ ] Dashboard carregando: `http://dominio:8005/dashboard/`
- [ ] Imagens aparecendo
- [ ] Formulários funcionando

#### **✅ Sistema Administrativo:**
- [ ] Login: admin / admin123
- [ ] Criação de produtos
- [ ] Gestão de pedidos
- [ ] Sistema de sorteio
- [ ] Upload de imagens

#### **✅ Sistema Público:**
- [ ] Fazer pedidos
- [ ] Upload de comprovantes
- [ ] Histórico de pedidos
- [ ] Detalhes de pedidos

### **🔧 Troubleshooting:**

#### **❌ Problemas Comuns:**
- [ ] Container não inicia → Verificar logs
- [ ] Porta não acessível → Verificar mapeamento 8005:8000
- [ ] Imagens não carregam → Verificar volume media
- [ ] Banco não funciona → Verificar migrações
- [ ] Arquivos estáticos → Verificar WhiteNoise

#### **✅ Comandos de Diagnóstico:**
```bash
# Ver logs do container
docker logs <container-name>

# Acessar container
docker exec -it <container-name> /bin/bash

# Verificar Django
python manage.py check

# Verificar banco
python manage.py dbshell

# Testar aplicação
curl http://localhost:8000/
```

### **🎯 Status Final:**

#### **✅ Sistema Funcionando:**
- [ ] Container rodando
- [ ] Porta 8005 acessível
- [ ] Django funcionando
- [ ] Banco de dados OK
- [ ] Arquivos estáticos OK
- [ ] Sistema completo funcional

### **📞 Suporte:**

#### **🔗 Links Úteis:**
- **Repositório:** https://github.com/alancarneiropt/sistema_cotas.git
- **Documentação:** `README.md`
- **Deploy:** `DEPLOY_EASYPANEL.md`
- **Configuração:** `easypanel.yml`

---

## 🎉 **Sistema Pronto para Deploy!**

**Todas as configurações foram verificadas e corrigidas para funcionar perfeitamente no Easypanel na porta 8005!** 🚀✨
