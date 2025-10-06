"""
Views públicas para a app raffles.
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from .forms import PublicOrderForm, ReceiptUploadForm
from .models import Product, Order, Quota
from .services import allocate_random_quotas

logger = logging.getLogger(__name__)


def home(request):
    """
    Página inicial com lista de produtos ativos e formulário de pedido.
    """
    products = Product.objects.filter(status=Product.ACTIVE).order_by("-created_at")
    
    if request.method == "POST":
        form = PublicOrderForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                product = form.cleaned_data["product"]
                quantity = form.cleaned_data["quantity"]
                
                # Calcula o valor total
                total_cents = quantity * product.price_cents
                
                # Cria o pedido base
                order = Order.objects.create(
                    product=product,
                    full_name=form.cleaned_data["full_name"],
                    email=form.cleaned_data.get("email", ""),
                    whatsapp=form.cleaned_data.get("whatsapp", ""),
                    quantity=quantity,
                    total_price_cents=total_cents,
                    status=Order.RESERVED,
                    receipt=form.cleaned_data.get("receipt")
                )
                
                try:
                    # Aloca cotas aleatórias
                    numbers = allocate_random_quotas(product.id, quantity, order)
                    
                    # Armazena informações na sessão para a página de sucesso
                    request.session["last_order_id"] = order.id
                    request.session["last_numbers"] = numbers
                    request.session["last_order_total"] = order.total_price_display
                    
                    logger.info(
                        f"Pedido {order.id} criado com sucesso. "
                        f"Cotas alocadas: {numbers}"
                    )
                    
                    return redirect(reverse("raffles:order_success"))
                    
                except Exception as e:
                    # Em caso de erro na alocação, cancela o pedido
                    order.status = Order.CANCELED
                    order.save(update_fields=["status"])
                    
                    logger.error(f"Erro ao alocar cotas para pedido {order.id}: {str(e)}")
                    
                    form.add_error(None, f"Não foi possível alocar cotas: {str(e)}")
                    
            except Exception as e:
                logger.error(f"Erro ao criar pedido: {str(e)}")
                form.add_error(None, f"Erro interno: {str(e)}")
    else:
        form = PublicOrderForm()
    
    context = {
        "products": products,
        "form": form,
    }
    
    return render(request, "raffles/public_home.html", context)


def order_success(request):
    """
    Página de sucesso após criação do pedido.
    """
    order_id = request.session.get("last_order_id")
    numbers = request.session.get("last_numbers", [])
    order_total = request.session.get("last_order_total", "")
    
    if not order_id:
        messages.warning(request, "Sessão expirada. Redirecionando para página inicial.")
        return redirect(reverse("raffles:home"))
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Pedido não encontrado.")
        return redirect(reverse("raffles:home"))
    
    # Limpa a sessão após exibir as informações
    for key in ["last_order_id", "last_numbers", "last_order_total"]:
        request.session.pop(key, None)
    
    context = {
        "order": order,
        "order_id": order_id,
        "numbers": numbers,
        "order_total": order_total,
        "reserve_expires_at": order.reserve_expires_at,
    }
    
    return render(request, "raffles/order_success.html", context)


def upload_receipt(request, order_id):
    """
    Página e processamento para upload de comprovante.
    """
    order = get_object_or_404(Order, id=order_id)
    
    if order.status not in [Order.RESERVED, Order.WAITING_CONFIRM]:
        messages.error(request, "Este pedido não pode receber comprovante no momento.")
        return redirect(reverse("raffles:home"))
    
    if order.is_expired:
        messages.error(request, "Pedido expirado.")
        return redirect(reverse("raffles:home"))
    
    if request.method == "POST":
        form = ReceiptUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                order.receipt = form.cleaned_data["receipt"]
                order.status = Order.WAITING_PROOF
                order.save(update_fields=["receipt", "status"])
                
                messages.success(request, "Comprovante enviado com sucesso!")
                
                logger.info(f"Comprovante enviado para pedido {order_id}")
                
                return redirect(reverse("raffles:upload_receipt", args=[order_id]))
                
            except Exception as e:
                logger.error(f"Erro ao salvar comprovante do pedido {order_id}: {str(e)}")
                messages.error(request, "Erro ao salvar comprovante. Tente novamente.")
    else:
        form = ReceiptUploadForm(initial={"order_id": order_id})
    
    context = {
        "order": order,
        "form": form,
    }
    
    return render(request, "raffles/upload_receipt.html", context)


def order_status(request, order_id):
    """
    Página para consultar status de um pedido.
    """
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        "order": order,
    }
    
    return render(request, "raffles/order_status.html", context)


def product_detail(request, product_id):
    """
    Página de detalhes de um produto específico.
    """
    product = get_object_or_404(Product, id=product_id, status=Product.ACTIVE)
    
    # Busca últimos pedidos para este produto (sem informações sensíveis)
    recent_orders = Order.objects.filter(
        product=product,
        status__in=[Order.CONFIRMED, Order.WAITING_CONFIRM]
    ).order_by("-created_at")[:10]
    
    # Formata nomes para privacidade
    for order in recent_orders:
        name_parts = order.full_name.split()
        if len(name_parts) >= 2:
            order.full_name = f"{name_parts[0]} {name_parts[-1][0]}."
        else:
            order.full_name = f"{name_parts[0][0]}."
    
    context = {
        "product": product,
        "recent_orders": recent_orders,
    }
    
    return render(request, "raffles/product_detail.html", context)


def winners_list(request):
    """
    Página com lista de produtos sorteados e vencedores.
    """
    products = Product.objects.filter(
        status=Product.CLOSED,
        drawn_number__isnull=False
    ).order_by("-draw_datetime")
    
    context = {
        "products": products,
    }
    
    return render(request, "raffles/winners_list.html", context)


@require_http_methods(["GET"])
def api_products_active(request):
    """
    API endpoint para listar produtos ativos (AJAX).
    """
    products = Product.objects.filter(status=Product.ACTIVE).order_by("-created_at")
    
    data = []
    for product in products:
        data.append({
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "price_cents": product.price_cents,
            "price_display": product.price_display,
            "total_quotas": product.total_quotas,
            "sold_count": product.sold_count,
            "reserved_count": product.reserved_count,
            "available_count": product.available_count,
            "progress_percentage": product.progress_percentage,
            "draw_datetime": product.draw_datetime.isoformat() if product.draw_datetime else None,
            "image_url": product.image.url if product.image else None,
        })
    
    return JsonResponse({"products": data})


@require_http_methods(["GET"])
def api_product_quotas(request, product_id):
    """
    API endpoint para consultar disponibilidade de cotas de um produto.
    """
    try:
        product = Product.objects.get(id=product_id, status=Product.ACTIVE)
        
        data = {
            "product_id": product.id,
            "title": product.title,
            "total_quotas": product.total_quotas,
            "sold_count": product.sold_count,
            "reserved_count": product.reserved_count,
            "available_count": product.available_count,
            "progress_percentage": product.progress_percentage,
        }
        
        return JsonResponse(data)
        
    except Product.DoesNotExist:
        return JsonResponse(
            {"error": "Produto não encontrado ou não está ativo"},
            status=404
        )


class ProductListView(TemplateView):
    """
    View baseada em classe para listar produtos (alternativa à função home).
    """
    template_name = "raffles/product_list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.filter(
            status=Product.ACTIVE
        ).order_by("-created_at")
        return context


def error_404(request, exception):
    """
    Página de erro 404 personalizada.
    """
    return render(request, "raffles/404.html", status=404)


def error_500(request):
    """
    Página de erro 500 personalizada.
    """
    return render(request, "raffles/500.html", status=500)


def order_history(request):
    """
    Página para consultar histórico de pedidos por nome, email ou telefone.
    """
    orders = []
    search_query = ""
    
    if request.method == "POST":
        search_query = request.POST.get("search", "").strip()
        
        if search_query:
            # Busca por nome, email ou WhatsApp
            orders = Order.objects.filter(
                Q(full_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(whatsapp__icontains=search_query)
            ).order_by("-created_at")
            
            if not orders.exists():
                messages.info(request, "Nenhum pedido encontrado com os critérios informados.")
    
    context = {
        "orders": orders,
        "search_query": search_query,
    }
    
    return render(request, "raffles/order_history.html", context)


def order_detail_full(request, order_id):
    """
    Página completa de detalhes do pedido com todas as informações.
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Busca todas as cotas do pedido
    quotas = Quota.objects.filter(order=order).order_by('number')
    
    context = {
        "order": order,
        "quotas": quotas,
    }
    
    return render(request, "raffles/order_detail_full.html", context)


@login_required
def admin_order_history(request):
    """
    Página administrativa para visualizar todos os pedidos com filtros.
    """
    orders = Order.objects.all().order_by("-created_at")
    
    # Filtros
    status_filter = request.GET.get("status", "")
    product_filter = request.GET.get("product", "")
    search_filter = request.GET.get("search", "")
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if product_filter:
        orders = orders.filter(product_id=product_filter)
    
    if search_filter:
        orders = orders.filter(
            Q(full_name__icontains=search_filter) |
            Q(email__icontains=search_filter) |
            Q(whatsapp__icontains=search_filter) |
            Q(id__icontains=search_filter)
        )
    
    # Paginação simples
    from django.core.paginator import Paginator
    paginator = Paginator(orders, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lista de produtos para filtro
    products = Product.objects.all().order_by("title")
    
    context = {
        "page_obj": page_obj,
        "orders": page_obj,
        "products": products,
        "status_filter": status_filter,
        "product_filter": product_filter,
        "search_filter": search_filter,
    }
    
    return render(request, "raffles/admin_order_history_modern.html", context)


@login_required
def admin_order_detail_full(request, order_id):
    """
    Página administrativa completa de detalhes do pedido.
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Busca todas as cotas do pedido
    quotas = Quota.objects.filter(order=order).order_by('number')
    
    # Histórico de mudanças (se implementado)
    # logs = AdminLog.objects.filter(details__order_id=order_id).order_by('-created_at')
    
    context = {
        "order": order,
        "quotas": quotas,
        # "logs": logs,
    }
    
    return render(request, "raffles/admin_order_detail_full.html", context)
