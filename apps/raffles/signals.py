"""
Signals para a app raffles.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Product, Quota

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
def create_quotas_on_product_activation(sender, instance, created, **kwargs):
    """
    Cria cotas automaticamente quando um produto é ativado.
    """
    # Só executa se o produto foi salvo e mudou para ativo
    if instance.status == Product.ACTIVE:
        # Verifica se já existem cotas para este produto
        existing_quotas = Quota.objects.filter(product=instance).count()
        
        if existing_quotas == 0 and instance.total_quotas > 0:
            try:
                # Cria as cotas usando bulk_create para eficiência
                quotas_to_create = []
                for number in range(1, instance.total_quotas + 1):
                    quotas_to_create.append(
                        Quota(
                            product=instance,
                            number=number,
                            status=Quota.AVAILABLE
                        )
                    )
                
                Quota.objects.bulk_create(quotas_to_create)
                
                logger.info(
                    f'Criadas {len(quotas_to_create)} cotas automaticamente '
                    f'para o produto {instance.title}'
                )
                
            except Exception as e:
                logger.error(
                    f'Erro ao criar cotas automaticamente para produto {instance.id}: {str(e)}'
                )


@receiver(pre_save, sender=Product)
def log_product_status_change(sender, instance, **kwargs):
    """
    Registra mudanças de status do produto.
    """
    if instance.pk:  # Produto existente
        try:
            old_instance = Product.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                logger.info(
                    f'Status do produto {instance.title} mudou de '
                    f'{old_instance.status} para {instance.status}'
                )
        except Product.DoesNotExist:
            pass  # Produto novo


@receiver(post_save, sender=Quota)
def log_quota_status_change(sender, instance, created, **kwargs):
    """
    Registra mudanças importantes no status das cotas.
    """
    if created:
        logger.debug(f'Nova cota criada: {instance.number} para produto {instance.product.title}')
    else:
        # Verifica se o status mudou
        try:
            old_instance = Quota.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                logger.info(
                    f'Status da cota {instance.number} (produto {instance.product.title}) '
                    f'mudou de {old_instance.status} para {instance.status}'
                )
        except Quota.DoesNotExist:
            pass
