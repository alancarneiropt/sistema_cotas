"""
Configuração do Celery para o projeto sistema_cotas.
"""
import os
from celery import Celery

# Define o módulo de configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cotas.settings')

app = Celery('sistema_cotas')

# Configuração usando strings para que o worker não tenha que
# serializar o objeto de configuração quando usar Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carrega tarefas de todas as apps registradas
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
