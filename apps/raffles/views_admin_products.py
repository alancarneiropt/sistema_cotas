"""
Views para CRUD de produtos no dashboard administrativo.
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone

from .models import Product, Quota
from .forms import ProductForm

logger = logging.getLogger(__name__)


@login_required
def admin_product_create(request):
    """
    Criar novo produto no dashboard.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            
            messages.success(request, f'Produto "{product.title}" criado com sucesso!')
            logger.info(f"Admin {request.user.username} criou produto {product.id}: {product.title}")
            
            return redirect(reverse('raffles:admin_product_detail', args=[product.id]))
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'action': 'create',
        'page_title': 'Criar Produto',
    }
    
    return render(request, 'raffles/admin_product_form.html', context)


@login_required
def admin_product_edit(request, product_id):
    """
    Editar produto existente no dashboard.
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.updated_at = timezone.now()
            product.save()
            
            messages.success(request, f'Produto "{product.title}" atualizado com sucesso!')
            logger.info(f"Admin {request.user.username} editou produto {product.id}: {product.title}")
            
            return redirect(reverse('raffles:admin_product_detail', args=[product.id]))
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'action': 'edit',
        'page_title': f'Editar: {product.title}',
    }
    
    return render(request, 'raffles/admin_product_form.html', context)


@login_required
def admin_product_delete(request, product_id):
    """
    Deletar produto (confirmação).
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_title = product.title
        product.delete()
        
        messages.success(request, f'Produto "{product_title}" deletado com sucesso!')
        logger.info(f"Admin {request.user.username} deletou produto {product_id}: {product_title}")
        
        return redirect(reverse('raffles:admin_products'))
    
    context = {
        'product': product,
    }
    
    return render(request, 'raffles/admin_product_delete.html', context)


@login_required
def admin_product_create_quotas(request, product_id):
    """
    Criar cotas para um produto.
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            from .management.commands.create_quotas import Command
            command = Command()
            command.handle(product_id=product_id)
            
            messages.success(request, f'{product.total_quotas} cotas criadas para "{product.title}"!')
            logger.info(f"Admin {request.user.username} criou {product.total_quotas} cotas para produto {product.id}")
            
        except Exception as e:
            messages.error(request, f'Erro ao criar cotas: {str(e)}')
            logger.error(f"Erro ao criar cotas para produto {product_id}: {str(e)}")
        
        return redirect(reverse('raffles:admin_product_detail', args=[product.id]))
    
    context = {
        'product': product,
    }
    
    return render(request, 'raffles/admin_product_create_quotas.html', context)


@login_required
def admin_product_toggle_status(request, product_id):
    """
    Alternar status do produto (ativo/inativo).
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        if product.status == Product.ACTIVE:
            product.status = Product.DRAFT
            status_text = "desativado"
        else:
            product.status = Product.ACTIVE
            status_text = "ativado"
        
        product.save()
        
        messages.success(request, f'Produto "{product.title}" {status_text} com sucesso!')
        logger.info(f"Admin {request.user.username} {status_text} produto {product.id}")
        
        return redirect(reverse('raffles:admin_product_detail', args=[product.id]))
    
    context = {
        'product': product,
    }
    
    return render(request, 'raffles/admin_product_toggle_status.html', context)
