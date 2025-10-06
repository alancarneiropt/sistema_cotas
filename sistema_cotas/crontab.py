"""
Configuração de tarefas cron para o projeto sistema_cotas.
"""

# Importa o CRONJOBS do settings
from .settings import CRONJOBS

# Tarefas que serão executadas via cron
CRONJOBS = [
    # Libera reservas expiradas a cada 5 minutos
    ('*/5 * * * *', 'django.core.management.call_command', ['release_expired_reservations']),
    
    # Gera relatório diário às 8h
    ('0 8 * * *', 'django.core.management.call_command', ['generate_daily_report']),
    
    # Limpa logs antigos semanalmente (domingo às 2h)
    ('0 2 * * 0', 'django.core.management.call_command', ['cleanup_old_logs']),
]
