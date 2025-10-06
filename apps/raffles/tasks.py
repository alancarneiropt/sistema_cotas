"""
Tasks do Celery para a app raffles.
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

from .services import release_expired_reservations
from .models import Order, Product

logger = logging.getLogger(__name__)


@shared_task
def release_expired_reservations_task():
    """
    Task periódica para liberar reservas expiradas.
    """
    try:
        released_quotas, expired_orders = release_expired_reservations()
        
        logger.info(
            f'Task liberou {released_quotas} cotas e expirou {expired_orders} pedidos'
        )
        
        return {
            'released_quotas': released_quotas,
            'expired_orders': expired_orders,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f'Erro na task de liberação de reservas: {str(e)}')
        raise


@shared_task
def send_order_confirmation_email(order_id):
    """
    Envia e-mail de confirmação de pedido.
    """
    try:
        order = Order.objects.get(id=order_id)
        
        subject = f'Pedido #{order_id} - Sistema de Cotas'
        message = f'''
        Olá {order.full_name},
        
        Seu pedido foi confirmado com sucesso!
        
        Detalhes do pedido:
        - Produto: {order.product.title}
        - Quantidade: {order.quantity} cota(s)
        - Valor total: {order.total_price_display}
        - Status: {order.get_status_display()}
        
        Suas cotas estão garantidas para o sorteio.
        
        Acompanhe o resultado em nosso site.
        
        Atenciosamente,
        Equipe Sistema de Cotas
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
        )
        
        logger.info(f'E-mail de confirmação enviado para pedido {order_id}')
        
    except Order.DoesNotExist:
        logger.error(f'Pedido {order_id} não encontrado para envio de e-mail')
    except Exception as e:
        logger.error(f'Erro ao enviar e-mail para pedido {order_id}: {str(e)}')


@shared_task
def send_draw_notification_email(product_id):
    """
    Envia notificação de sorteio realizado.
    """
    try:
        product = Product.objects.get(id=product_id)
        
        if not product.drawn_number:
            logger.error(f'Produto {product_id} não tem número sorteado')
            return
        
        # Busca o vencedor
        winning_quota = product.quotas.filter(number=product.drawn_number).first()
        if not winning_quota or not winning_quota.order:
            logger.error(f'Vencedor não encontrado para produto {product_id}')
            return
        
        winner_order = winning_quota.order
        
        subject = f'Sorteio Realizado - {product.title}'
        message = f'''
        Olá {winner_order.full_name},
        
        Parabéns! Você ganhou o sorteio!
        
        Detalhes do sorteio:
        - Produto: {product.title}
        - Número sorteado: {product.drawn_number}
        - Sua cota vencedora: {product.drawn_number}
        
        Entre em contato conosco para receber seu prêmio.
        
        Atenciosamente,
        Equipe Sistema de Cotas
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [winner_order.email],
            fail_silently=False,
        )
        
        logger.info(f'Notificação de vitória enviada para {winner_order.full_name}')
        
    except Product.DoesNotExist:
        logger.error(f'Produto {product_id} não encontrado')
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de sorteio: {str(e)}')


@shared_task
def cleanup_old_logs():
    """
    Remove logs antigos para manter o banco limpo.
    """
    try:
        from .models import AdminLog
        
        # Remove logs com mais de 30 dias
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        deleted_count = AdminLog.objects.filter(created_at__lt=cutoff_date).delete()[0]
        
        logger.info(f'Removidos {deleted_count} logs antigos')
        
        return {'deleted_logs': deleted_count}
        
    except Exception as e:
        logger.error(f'Erro na limpeza de logs: {str(e)}')
        raise


@shared_task
def generate_daily_report():
    """
    Gera relatório diário de vendas e estatísticas.
    """
    try:
        from datetime import datetime, timedelta
        
        yesterday = timezone.now() - timezone.timedelta(days=1)
        
        # Estatísticas do dia
        orders_today = Order.objects.filter(
            created_at__date=yesterday.date()
        )
        
        confirmed_orders = orders_today.filter(status=Order.CONFIRMED)
        total_revenue = sum(order.total_price_cents for order in confirmed_orders)
        
        # Produtos ativos
        active_products = Product.objects.filter(status=Product.ACTIVE).count()
        
        report = {
            'date': yesterday.date().isoformat(),
            'total_orders': orders_today.count(),
            'confirmed_orders': confirmed_orders.count(),
            'total_revenue_cents': total_revenue,
            'total_revenue_display': f'R$ {total_revenue / 100:.2f}',
            'active_products': active_products,
        }
        
        logger.info(f'Relatório diário gerado: {report}')
        
        return report
        
    except Exception as e:
        logger.error(f'Erro ao gerar relatório diário: {str(e)}')
        raise
