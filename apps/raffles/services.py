"""
Serviços para alocação e gerenciamento de cotas.
"""
import secrets
import logging
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Product, Order, Quota, AdminLog

logger = logging.getLogger(__name__)

# Configurações
RESERVE_MINUTES = 15  # Tempo de reserva em minutos


def _random_pick(queryset, k):
    """
    Seleciona k IDs distintos aleatórios de um QuerySet sem carregar tudo na memória.
    Usa algoritmo Fisher-Yates parcial para eficiência.
    """
    # Limita a 10000 IDs para proteção contra queries muito grandes
    ids = list(queryset.values_list("id", flat=True)[:10000])
    n = len(ids)
    
    if k > n:
        raise ValueError("Não há cotas suficientes disponíveis.")
    
    if k == 0:
        return []
    
    # Fisher–Yates shuffle parcial
    for i in range(k):
        j = i + secrets.randbelow(n - i)
        ids[i], ids[j] = ids[j], ids[i]
    
    return ids[:k]


@transaction.atomic
def allocate_random_quotas(product_id: int, quantity: int, order: Order):
    """
    Aloca cotas aleatórias para um pedido.
    
    Args:
        product_id: ID do produto
        quantity: Quantidade de cotas a alocar
        order: Instância do pedido
        
    Returns:
        list: Lista dos números das cotas alocadas
        
    Raises:
        ValueError: Se não houver cotas suficientes
        ValidationError: Se o produto não estiver ativo
    """
    now = timezone.now()
    
    try:
        # Bloqueia o produto para evitar condições de corrida
        product = Product.objects.select_for_update().get(
            id=product_id,
            status=Product.ACTIVE
        )
    except Product.DoesNotExist:
        raise ValidationError("Produto não encontrado ou não está ativo.")
    
    # QuerySet para cotas disponíveis com bloqueio
    available_qs = (
        Quota.objects
        .select_for_update(skip_locked=True)
        .filter(product=product, status=Quota.AVAILABLE)
        .order_by("id")
    )
    
    available_count = available_qs.count()
    if available_count < quantity:
        raise ValueError(
            f"Não há cotas suficientes. "
            f"Disponíveis: {available_count}, Solicitadas: {quantity}"
        )
    
    # Seleciona cotas aleatórias
    picked_ids = _random_pick(available_qs, quantity)
    
    # Calcula quando a reserva expira
    reserved_until = now + timezone.timedelta(minutes=RESERVE_MINUTES)
    
    # Atualiza as cotas selecionadas
    Quota.objects.filter(id__in=picked_ids).update(
        status=Quota.RESERVED,
        order=order,
        reserved_until=reserved_until
    )
    
    # Atualiza o pedido
    order.status = Order.WAITING_CONFIRM
    order.reserve_expires_at = reserved_until
    order.save(update_fields=["status", "reserve_expires_at"])
    
    # Busca os números das cotas alocadas
    picked_quotas = Quota.objects.filter(id__in=picked_ids)
    numbers = sorted(q.number for q in picked_quotas)
    
    logger.info(
        f"Alocadas {len(numbers)} cotas para pedido {order.id}: {numbers}"
    )
    
    return numbers


def release_expired_reservations():
    """
    Libera cotas com reservas expiradas e marca pedidos como expirados.
    
    Returns:
        tuple: (cotas_liberadas, pedidos_expirados)
    """
    now = timezone.now()
    
    with transaction.atomic():
        # Libera cotas expiradas
        released_quotas = Quota.objects.filter(
            status=Quota.RESERVED,
            reserved_until__lt=now
        ).update(
            status=Quota.AVAILABLE,
            order=None,
            reserved_until=None
        )
        
        # Marca pedidos como expirados
        expired_orders = Order.objects.filter(
            status__in=[Order.RESERVED, Order.WAITING_CONFIRM],
            reserve_expires_at__lt=now
        ).update(status=Order.EXPIRED)
        
        logger.info(
            f"Liberadas {released_quotas} cotas e expirados {expired_orders} pedidos"
        )
        
        return released_quotas, expired_orders


def confirm_order(order_id: int, admin_user=None):
    """
    Confirma um pedido e marca suas cotas como vendidas.
    
    Args:
        order_id: ID do pedido
        admin_user: Usuário administrador que confirmou
        
    Returns:
        bool: True se confirmado com sucesso
        
    Raises:
        ValidationError: Se o pedido não puder ser confirmado
    """
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            
            if order.status not in [Order.RESERVED, Order.WAITING_CONFIRM]:
                raise ValidationError(
                    f"Pedido não pode ser confirmado. Status atual: {order.status}"
                )
            
            if order.is_expired:
                raise ValidationError("Pedido expirado. Não pode ser confirmado.")
            
            # Atualiza status do pedido
            order.status = Order.CONFIRMED
            order.save(update_fields=["status"])
            
            # Marca cotas como vendidas
            updated_quotas = Quota.objects.filter(
                order=order,
                status=Quota.RESERVED
            ).update(
                status=Quota.SOLD,
                reserved_until=None
            )
            
            # Log da ação
            AdminLog.objects.create(
                admin_id=str(admin_user.id) if admin_user else "system",
                action="order_confirmed",
                details={
                    "order_id": order_id,
                    "quotas_updated": updated_quotas,
                    "product_id": order.product.id
                }
            )
            
            logger.info(
                f"Pedido {order_id} confirmado. "
                f"Atualizadas {updated_quotas} cotas."
            )
            
            return True
            
    except Order.DoesNotExist:
        raise ValidationError("Pedido não encontrado.")
    except Exception as e:
        logger.error(f"Erro ao confirmar pedido {order_id}: {str(e)}")
        raise ValidationError(f"Erro interno: {str(e)}")


def cancel_order(order_id: int, admin_user=None):
    """
    Cancela um pedido e libera suas cotas.
    
    Args:
        order_id: ID do pedido
        admin_user: Usuário administrador que cancelou
        
    Returns:
        bool: True se cancelado com sucesso
    """
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            
            if order.status == Order.CANCELED:
                return True  # Já está cancelado
            
            # Atualiza status do pedido
            order.status = Order.CANCELED
            order.save(update_fields=["status"])
            
            # Libera cotas reservadas
            released_quotas = Quota.objects.filter(
                order=order,
                status=Quota.RESERVED
            ).update(
                status=Quota.AVAILABLE,
                order=None,
                reserved_until=None
            )
            
            # Log da ação
            AdminLog.objects.create(
                admin_id=str(admin_user.id) if admin_user else "system",
                action="order_canceled",
                details={
                    "order_id": order_id,
                    "quotas_released": released_quotas,
                    "product_id": order.product.id
                }
            )
            
            logger.info(
                f"Pedido {order_id} cancelado. "
                f"Liberadas {released_quotas} cotas."
            )
            
            return True
            
    except Order.DoesNotExist:
        raise ValidationError("Pedido não encontrado.")
    except Exception as e:
        logger.error(f"Erro ao cancelar pedido {order_id}: {str(e)}")
        raise ValidationError(f"Erro interno: {str(e)}")


def draw_winner(product_id: int, draw_source: str = "", admin_user=None):
    """
    Realiza o sorteio de um produto e define o vencedor.
    
    Args:
        product_id: ID do produto
        draw_source: Descrição de como foi realizado o sorteio
        admin_user: Usuário administrador que realizou o sorteio
        
    Returns:
        dict: Informações do vencedor
        
    Raises:
        ValidationError: Se o sorteio não puder ser realizado
    """
    try:
        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=product_id)
            
            if product.status != Product.ACTIVE:
                raise ValidationError(
                    "Produto deve estar ativo para realizar o sorteio."
                )
            
            if product.drawn_number is not None:
                raise ValidationError("Sorteio já foi realizado para este produto.")
            
            # Busca cotas vendidas
            sold_quotas = Quota.objects.filter(
                product=product,
                status=Quota.SOLD
            )
            
            if not sold_quotas.exists():
                raise ValidationError("Não há cotas vendidas para sortear.")
            
            # Sorteia um número aleatório
            quota_numbers = list(sold_quotas.values_list('number', flat=True))
            drawn_number = secrets.choice(quota_numbers)
            
            # Busca a cota sorteada e o pedido
            winning_quota = sold_quotas.get(number=drawn_number)
            winning_order = winning_quota.order
            
            # Atualiza o produto
            product.drawn_number = drawn_number
            product.draw_source = draw_source
            product.status = Product.CLOSED
            product.save(update_fields=["drawn_number", "draw_source", "status"])
            
            # Log da ação
            AdminLog.objects.create(
                admin_id=str(admin_user.id) if admin_user else "system",
                action="draw_completed",
                details={
                    "product_id": product_id,
                    "drawn_number": drawn_number,
                    "winning_order_id": winning_order.id,
                    "total_sold": len(quota_numbers)
                }
            )
            
            winner_info = {
                "drawn_number": drawn_number,
                "winner_name": winning_order.full_name,
                "winner_email": winning_order.email,
                "winner_whatsapp": winning_order.whatsapp,
                "order_id": winning_order.id,
                "total_sold": len(quota_numbers)
            }
            
            logger.info(
                f"Sorteio realizado para {product.title}. "
                f"Número sorteado: {drawn_number}. "
                f"Vencedor: {winning_order.full_name}"
            )
            
            return winner_info
            
    except Product.DoesNotExist:
        raise ValidationError("Produto não encontrado.")
    except Exception as e:
        logger.error(f"Erro ao realizar sorteio do produto {product_id}: {str(e)}")
        raise ValidationError(f"Erro interno: {str(e)}")


def create_product_quotas(product_id: int):
    """
    Cria todas as cotas para um produto (1 até total_quotas).
    
    Args:
        product_id: ID do produto
        
    Returns:
        int: Número de cotas criadas
    """
    try:
        product = Product.objects.get(id=product_id)
        
        # Verifica se já existem cotas
        existing_count = Quota.objects.filter(product=product).count()
        if existing_count > 0:
            logger.warning(
                f"Produto {product_id} já possui {existing_count} cotas. "
                "Não foram criadas novas cotas."
            )
            return 0
        
        # Cria as cotas
        quotas_to_create = []
        for number in range(1, product.total_quotas + 1):
            quotas_to_create.append(
                Quota(
                    product=product,
                    number=number,
                    status=Quota.AVAILABLE
                )
            )
        
        Quota.objects.bulk_create(quotas_to_create)
        
        logger.info(
            f"Criadas {product.total_quotas} cotas para o produto {product.title}"
        )
        
        return product.total_quotas
        
    except Product.DoesNotExist:
        raise ValidationError("Produto não encontrado.")
    except Exception as e:
        logger.error(f"Erro ao criar cotas para produto {product_id}: {str(e)}")
        raise ValidationError(f"Erro interno: {str(e)}")
