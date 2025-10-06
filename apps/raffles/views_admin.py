"""
Views administrativas para a app raffles.
"""
import logging
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.db.models import Count, Q

from .models import Product, Order, Quota, AdminLog
from .forms import ProductForm, OrderStatusForm
from .services import (
    confirm_order, cancel_order, draw_winner, 
    create_product_quotas, release_expired_reservations
)

logger = logging.getLogger(__name__)


@login_required
def admin_dashboard(request, product_id=None):
    """
    Dashboard administrativo principal.
    """
    products = Product.objects.all().order_by("-created_at")
    
    if product_id is None:
        product = products.first() if products.exists() else None
    else:
        product = get_object_or_404(Product, id=product_id)
    
    # Estatísticas gerais
    total_products = Product.objects.count()
    active_products = Product.objects.filter(status=Product.ACTIVE).count()
    closed_products = Product.objects.filter(status=Product.CLOSED).count()
    
    # Estatísticas do produto selecionado
    if product:
        total_quotas = product.total_quotas
        sold_count = product.sold_count
        reserved_count = product.reserved_count
        available_count = product.available_count
        progress_percentage = getattr(product, 'progress_percentage', 0)
        
        # Pedidos recentes para o produto
        recent_orders = Order.objects.filter(
            product=product
        ).order_by("-created_at")[:50]
        
        # Estatísticas de pedidos
        orders_stats = Order.objects.filter(product=product).aggregate(
            total_orders=Count('id'),
            confirmed_orders=Count('id', filter=Q(status=Order.CONFIRMED)),
            pending_orders=Count('id', filter=Q(status__in=[
                Order.RESERVED, Order.WAITING_CONFIRM, Order.WAITING_PROOF
            ])),
            expired_orders=Count('id', filter=Q(status=Order.EXPIRED)),
            canceled_orders=Count('id', filter=Q(status=Order.CANCELED)),
        )
        
        # Receita total (apenas pedidos confirmados)
        confirmed_orders = Order.objects.filter(
            product=product,
            status=Order.CONFIRMED
        )
        total_revenue_cents = sum(order.total_price_cents for order in confirmed_orders)
        total_revenue = f"R$ {total_revenue_cents / 100:.2f}".replace('.', ',')
        
    else:
        total_quotas = sold_count = reserved_count = available_count = 0
        progress_percentage = 0
        recent_orders = []
        orders_stats = {}
        total_revenue = "R$ 0,00"
    
    context = {
        "products": products,
        "product": product,
        "total_products": total_products,
        "active_products": active_products,
        "closed_products": closed_products,
        "total_quotas": total_quotas,
        "sold_count": sold_count,
        "reserved_count": reserved_count,
        "available_count": available_count,
        "progress_percentage": progress_percentage,
        "recent_orders": recent_orders,
        "orders_stats": orders_stats,
        "total_revenue": total_revenue,
    }
    
    return render(request, "raffles/dashboard_modern.html", context)


@login_required
def admin_products(request):
    """
    Lista e gerencia produtos.
    """
    products = Product.objects.all().order_by("-created_at")
    
    context = {
        "products": products,
    }
    
    return render(request, "raffles/admin_products.html", context)


@login_required
def admin_product_detail(request, product_id):
    """
    Detalhes de um produto específico no admin.
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Pedidos para este produto
    orders = Order.objects.filter(product=product).order_by("-created_at")
    
    # Estatísticas de cotas
    quota_stats = Quota.objects.filter(product=product).aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(status=Quota.AVAILABLE)),
        reserved=Count('id', filter=Q(status=Quota.RESERVED)),
        sold=Count('id', filter=Q(status=Quota.SOLD)),
    )
    
    # Informações do vencedor se o produto foi sorteado
    winner_info = None
    if product.drawn_number:
        try:
            winning_quota = Quota.objects.get(
                product=product, 
                number=product.drawn_number
            )
            if winning_quota.order:
                winner_info = {
                    'order': winning_quota.order,
                    'quota_number': product.drawn_number,
                    'winner_name': winning_quota.order.full_name,
                    'winner_email': winning_quota.order.email,
                    'winner_whatsapp': winning_quota.order.whatsapp,
                }
        except Quota.DoesNotExist:
            pass
    
    context = {
        "product": product,
        "orders": orders,
        "quota_stats": quota_stats,
        "winner_info": winner_info,
    }
    
    return render(request, "raffles/admin_product_detail.html", context)


@login_required
def admin_orders(request):
    """
    Lista e gerencia pedidos.
    """
    orders = Order.objects.all().order_by("-created_at")
    
    # Filtros
    status_filter = request.GET.get('status')
    product_filter = request.GET.get('product')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if product_filter:
        orders = orders.filter(product_id=product_filter)
    
    # Estatísticas
    orders_stats = Order.objects.aggregate(
        total=Count('id'),
        confirmed=Count('id', filter=Q(status=Order.CONFIRMED)),
        pending=Count('id', filter=Q(status__in=[
            Order.RESERVED, Order.WAITING_CONFIRM, Order.WAITING_PROOF
        ])),
        expired=Count('id', filter=Q(status=Order.EXPIRED)),
        canceled=Count('id', filter=Q(status=Order.CANCELED)),
    )
    
    products = Product.objects.all().order_by('title')
    
    context = {
        "orders": orders[:100],  # Limita a 100 para performance
        "orders_stats": orders_stats,
        "products": products,
        "status_filter": status_filter,
        "product_filter": product_filter,
    }
    
    return render(request, "raffles/admin_orders.html", context)


@login_required
def admin_order_detail(request, order_id):
    """
    Detalhes de um pedido específico no admin.
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Cotas do pedido
    quotas = Quota.objects.filter(order=order).order_by('number')
    
    context = {
        "order": order,
        "quotas": quotas,
    }
    
    return render(request, "raffles/admin_order_detail.html", context)


@login_required
def confirm_order_action(request, order_id):
    """
    Ação para confirmar um pedido.
    """
    try:
        success = confirm_order(order_id, admin_user=request.user)
        
        if success:
            messages.success(request, f"Pedido #{order_id} confirmado com sucesso!")
        else:
            messages.error(request, f"Erro ao confirmar pedido #{order_id}")
            
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        logger.error(f"Erro ao confirmar pedido {order_id}: {str(e)}")
        messages.error(request, f"Erro interno: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', reverse('raffles:admin_orders')))


@login_required
def cancel_order_action(request, order_id):
    """
    Ação para cancelar um pedido.
    """
    try:
        success = cancel_order(order_id, admin_user=request.user)
        
        if success:
            messages.success(request, f"Pedido #{order_id} cancelado com sucesso!")
        else:
            messages.error(request, f"Erro ao cancelar pedido #{order_id}")
            
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        logger.error(f"Erro ao cancelar pedido {order_id}: {str(e)}")
        messages.error(request, f"Erro interno: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', reverse('raffles:admin_orders')))


@login_required
def draw_product_action(request, product_id):
    """
    Ação para realizar o sorteio de um produto.
    """
    if request.method != "POST":
        return redirect(request.META.get('HTTP_REFERER', reverse('raffles:admin_dashboard')))
    
    draw_source = request.POST.get('draw_source', 'Sorteio realizado pelo administrador')
    
    try:
        winner_info = draw_winner(product_id, draw_source, admin_user=request.user)
        
        messages.success(
            request,
            f"🎉 Sorteio realizado com sucesso! Número sorteado: {winner_info['drawn_number']}. "
            f"Vencedor: {winner_info['winner_name']}"
        )
        
        # Log da ação
        AdminLog.objects.create(
            admin_id=str(request.user.id),
            action="draw_completed",
            details={
                "product_id": product_id,
                "drawn_number": winner_info['drawn_number'],
                "winner_name": winner_info['winner_name'],
                "winner_order_id": winner_info['order_id']
            }
        )
        
        # Redireciona para a página de detalhes do produto para mostrar o vencedor
        return redirect(reverse('raffles:admin_product_detail', args=[product_id]))
        
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        logger.error(f"Erro ao realizar sorteio do produto {product_id}: {str(e)}")
        messages.error(request, f"Erro interno: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', reverse('raffles:admin_dashboard')))


@login_required
def create_quotas_action(request, product_id):
    """
    Ação para criar cotas para um produto.
    """
    try:
        quotas_created = create_product_quotas(product_id)
        
        messages.success(
            request,
            f"Criadas {quotas_created} cotas para o produto com sucesso!"
        )
        
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        logger.error(f"Erro ao criar cotas para produto {product_id}: {str(e)}")
        messages.error(request, f"Erro interno: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', reverse('raffles:admin_products')))


@login_required
def release_reservations_action(request):
    """
    Ação para liberar reservas expiradas.
    """
    try:
        released_quotas, expired_orders = release_expired_reservations()
        
        messages.success(
            request,
            f"Liberadas {released_quotas} cotas e expirados {expired_orders} pedidos."
        )
        
    except Exception as e:
        logger.error(f"Erro ao liberar reservas expiradas: {str(e)}")
        messages.error(request, f"Erro interno: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', reverse('raffles:admin_dashboard')))


@login_required
@require_http_methods(["GET"])
def admin_stats_api(request):
    """
    API para estatísticas em tempo real do dashboard.
    """
    try:
        # Estatísticas gerais
        stats = {
            "total_products": Product.objects.count(),
            "active_products": Product.objects.filter(status=Product.ACTIVE).count(),
            "closed_products": Product.objects.filter(status=Product.CLOSED).count(),
            "total_orders": Order.objects.count(),
            "confirmed_orders": Order.objects.filter(status=Order.CONFIRMED).count(),
            "pending_orders": Order.objects.filter(status__in=[
                Order.RESERVED, Order.WAITING_CONFIRM, Order.WAITING_PROOF
            ]).count(),
            "expired_orders": Order.objects.filter(status=Order.EXPIRED).count(),
        }
        
        # Receita total
        confirmed_orders = Order.objects.filter(status=Order.CONFIRMED)
        total_revenue_cents = sum(order.total_price_cents for order in confirmed_orders)
        stats["total_revenue"] = f"R$ {total_revenue_cents / 100:.2f}".replace('.', ',')
        
        return JsonResponse(stats)
        
    except Exception as e:
        logger.error(f"Erro na API de estatísticas: {str(e)}")
        return JsonResponse({"error": "Erro interno"}, status=500)


@login_required
def admin_logs(request):
    """
    Visualização de logs administrativos.
    """
    logs = AdminLog.objects.all().order_by("-created_at")[:200]
    
    context = {
        "logs": logs,
    }
    
    return render(request, "raffles/admin_logs.html", context)


class AdminDashboardView(TemplateView):
    """
    View baseada em classe para o dashboard administrativo.
    """
    template_name = "raffles/admin_dashboard.html"
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        products = Product.objects.all().order_by("-created_at")
        context["products"] = products
        
        if products.exists():
            product = products.first()
            context["product"] = product
            context["total_quotas"] = product.total_quotas
            context["sold_count"] = product.sold_count
            context["reserved_count"] = product.reserved_count
            context["available_count"] = product.available_count
            context["progress_percentage"] = product.progress_percentage
        
        return context


@login_required
def confirm_order_with_receipt(request, order_id):
    """
    Confirma um pedido que tem comprovante de pagamento.
    """
    order = get_object_or_404(Order, id=order_id)
    
    if order.status not in [Order.WAITING_PROOF, Order.WAITING_CONFIRM]:
        messages.error(request, "Este pedido não pode ser confirmado no momento.")
        return redirect(reverse("raffles:admin_order_detail", args=[order_id]))
    
    if not order.receipt:
        messages.error(request, "Este pedido não possui comprovante de pagamento.")
        return redirect(reverse("raffles:admin_order_detail", args=[order_id]))
    
    try:
        # Confirma o pedido
        order.status = Order.CONFIRMED
        order.save(update_fields=["status"])
        
        # Atualiza todas as cotas do pedido para vendidas
        quotas = Quota.objects.filter(order=order)
        quotas.update(
            status=Quota.SOLD,
            reserved_until=None
        )
        
        # Registra no log
        AdminLog.objects.create(
            admin_id=str(request.user.id),
            action="Confirmar Pedido com Comprovante",
            details={
                "order_id": order_id,
                "customer_name": order.full_name,
                "product": order.product.title,
                "quotas_count": quotas.count(),
                "quotas_numbers": list(quotas.values_list('number', flat=True)),
                "admin_user": request.user.username
            }
        )
        
        messages.success(
            request, 
            f"Pedido #{order_id} confirmado com sucesso! "
            f"{quotas.count()} cotas foram marcadas como vendidas."
        )
        
        logger.info(f"Admin {request.user.username} confirmou pedido {order_id} com comprovante")
        
    except Exception as e:
        logger.error(f"Erro ao confirmar pedido {order_id}: {str(e)}")
        messages.error(request, f"Erro ao confirmar pedido: {str(e)}")
    
    return redirect(reverse("raffles:admin_order_detail", args=[order_id]))


@login_required
def confirm_order_without_receipt(request, order_id):
    """
    Confirma um pedido sem comprovante de pagamento (confiança).
    """
    order = get_object_or_404(Order, id=order_id)
    
    if order.status not in [Order.RESERVED, Order.WAITING_CONFIRM]:
        messages.error(request, "Este pedido não pode ser confirmado no momento.")
        return redirect(reverse("raffles:admin_order_detail", args=[order_id]))
    
    try:
        # Confirma o pedido
        order.status = Order.CONFIRMED
        order.save(update_fields=["status"])
        
        # Atualiza todas as cotas do pedido para vendidas
        quotas = Quota.objects.filter(order=order)
        quotas.update(
            status=Quota.SOLD,
            reserved_until=None
        )
        
        # Registra no log
        AdminLog.objects.create(
            admin_id=str(request.user.id),
            action="Confirmar Pedido sem Comprovante",
            details={
                "order_id": order_id,
                "customer_name": order.full_name,
                "product": order.product.title,
                "quotas_count": quotas.count(),
                "quotas_numbers": list(quotas.values_list('number', flat=True)),
                "admin_user": request.user.username,
                "note": "Confirmação por confiança - sem comprovante"
            }
        )
        
        messages.success(
            request, 
            f"Pedido #{order_id} confirmado por confiança! "
            f"{quotas.count()} cotas foram marcadas como vendidas. "
            f"⚠️ ATENÇÃO: Este pedido foi confirmado sem comprovante."
        )
        
        logger.info(f"Admin {request.user.username} confirmou pedido {order_id} sem comprovante")
        
    except Exception as e:
        logger.error(f"Erro ao confirmar pedido {order_id}: {str(e)}")
        messages.error(request, f"Erro ao confirmar pedido: {str(e)}")
    
    return redirect(reverse("raffles:admin_order_detail", args=[order_id]))
