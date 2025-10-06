"""
Management command para liberar reservas expiradas.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import logging

from apps.raffles.models import Quota, Order
from apps.raffles.services import release_expired_reservations

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Libera cotas reservadas com prazo expirado e expira pedidos."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a execução sem fazer alterações no banco de dados',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra informações detalhadas sobre as operações',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('=== LIBERADOR DE RESERVAS EXPIRADAS ===')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO SIMULAÇÃO - Nenhuma alteração será feita')
            )
        
        # Busca reservas expiradas
        now = timezone.now()
        
        # Cotas expiradas
        expired_quotas = Quota.objects.filter(
            status=Quota.RESERVED,
            reserved_until__lt=now
        ).select_related('product', 'order')
        
        # Pedidos expirados
        expired_orders = Order.objects.filter(
            status__in=[Order.RESERVED, Order.WAITING_CONFIRM],
            reserve_expires_at__lt=now
        ).select_related('product')
        
        quota_count = expired_quotas.count()
        order_count = expired_orders.count()
        
        self.stdout.write(f'Cotas expiradas encontradas: {quota_count}')
        self.stdout.write(f'Pedidos expirados encontrados: {order_count}')
        
        if quota_count == 0 and order_count == 0:
            self.stdout.write(
                self.style.SUCCESS('Nenhuma reserva expirada encontrada.')
            )
            return
        
        if verbose:
            self._show_detailed_info(expired_quotas, expired_orders)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Simulação concluída. Use sem --dry-run para executar.')
            )
            return
        
        # Executa a liberação
        try:
            with transaction.atomic():
                released_quotas, expired_orders_count = release_expired_reservations()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Liberadas {released_quotas} cotas'
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Expiraos {expired_orders_count} pedidos'
                    )
                )
                
                if verbose:
                    self._log_operations(expired_quotas, expired_orders)
                
        except Exception as e:
            logger.error(f'Erro ao liberar reservas expiradas: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Erro ao executar operação: {str(e)}')
            )
            raise

    def _show_detailed_info(self, expired_quotas, expired_orders):
        """Mostra informações detalhadas sobre as reservas expiradas."""
        self.stdout.write('\n--- COTAS EXPIRADAS ---')
        
        for quota in expired_quotas[:10]:  # Limita a 10 para não sobrecarregar
            self.stdout.write(
                f'  Cota {quota.number} do produto "{quota.product.title}" '
                f'(Pedido #{quota.order.id if quota.order else "N/A"}) - '
                f'Expirou em {quota.reserved_until.strftime("%d/%m/%Y %H:%M")}'
            )
        
        if expired_quotas.count() > 10:
            self.stdout.write(f'  ... e mais {expired_quotas.count() - 10} cotas')
        
        self.stdout.write('\n--- PEDIDOS EXPIRADOS ---')
        
        for order in expired_orders[:10]:  # Limita a 10
            self.stdout.write(
                f'  Pedido #{order.id} - {order.full_name} '
                f'({order.product.title}) - '
                f'Expirou em {order.reserve_expires_at.strftime("%d/%m/%Y %H:%M")}'
            )
        
        if expired_orders.count() > 10:
            self.stdout.write(f'  ... e mais {expired_orders.count() - 10} pedidos')

    def _log_operations(self, expired_quotas, expired_orders):
        """Registra as operações realizadas."""
        self.stdout.write('\n--- OPERAÇÕES REALIZADAS ---')
        
        # Log das cotas liberadas
        for quota in expired_quotas:
            logger.info(
                f'Cota {quota.number} liberada do produto {quota.product.title} '
                f'(Pedido #{quota.order.id if quota.order else "N/A"})'
            )
        
        # Log dos pedidos expirados
        for order in expired_orders:
            logger.info(
                f'Pedido #{order.id} expirado - {order.full_name} '
                f'({order.product.title})'
            )
        
        self.stdout.write('Logs detalhados salvos no arquivo de log do sistema.')
