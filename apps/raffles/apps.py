"""
Configuração da app raffles.
"""
from django.apps import AppConfig


class RafflesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.raffles'
    verbose_name = 'Sistema de Cotas'

    def ready(self):
        """Importa os signals quando a app estiver pronta."""
        import apps.raffles.signals
