"""
Configuração do Django Admin para a app raffles.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Count
from django.utils import timezone

from .models import Product, Order, Quota, AdminLog
from .services import confirm_order, cancel_order, draw_winner, create_product_quotas


class QuotaInline(admin.TabularInline):
    """Inline para exibir cotas no admin de produtos."""
    model = Quota
    extra = 0
    readonly_fields = ('number', 'status', 'order_link', 'reserved_until')
    fields = ('number', 'status', 'order_link', 'reserved_until')
    can_delete = False
    
    def order_link(self, obj):
        """Link para o pedido da cota."""
        if obj.order:
            url = reverse('admin:raffles_order_change', args=[obj.order.id])
            return format_html('<a href="{}">Pedido #{}</a>', url, obj.order.id)
        return '-'
    order_link.short_description = 'Pedido'
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin para produtos."""
    
    list_display = (
        'title', 'status', 'price_display', 'total_quotas', 
        'quotas_summary', 'progress_bar', 'draw_datetime', 'created_at'
    )
    list_filter = ('status', 'created_at', 'draw_datetime')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'drawn_number', 'progress_display')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'description', 'image')
        }),
        ('Configurações', {
            'fields': ('price_cents', 'total_quotas', 'status')
        }),
        ('Sorteio', {
            'fields': ('draw_datetime', 'drawn_number', 'draw_source')
        }),
        ('Estatísticas', {
            'fields': ('progress_display',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [QuotaInline]
    actions = ['create_quotas_action', 'activate_products', 'close_products']
    
    def price_display(self, obj):
        """Exibe o preço formatado."""
        return obj.price_display
    price_display.short_description = 'Preço'
    price_display.admin_order_field = 'price_cents'
    
    def quotas_summary(self, obj):
        """Resumo das cotas."""
        return format_html(
            '<span style="color: green;">V: {}</span> | '
            '<span style="color: orange;">R: {}</span> | '
            '<span style="color: blue;">D: {}</span>',
            obj.sold_count, obj.reserved_count, obj.available_count
        )
    quotas_summary.short_description = 'Vendidas | Reservadas | Disponíveis'
    
    def progress_bar(self, obj):
        """Barra de progresso das vendas."""
        percentage = obj.progress_percentage
        color = 'success' if percentage >= 80 else 'warning' if percentage >= 50 else 'info'
        return format_html(
            '<div class="progress" style="width: 100px;"><div class="progress-bar bg-{}" '
            'style="width: {}%"></div></div> {}%',
            color, percentage, percentage
        )
    progress_bar.short_description = 'Progresso'
    
    def progress_display(self, obj):
        """Estatísticas detalhadas."""
        return format_html(
            '<strong>Vendidas:</strong> {}<br>'
            '<strong>Reservadas:</strong> {}<br>'
            '<strong>Disponíveis:</strong> {}<br>'
            '<strong>Progresso:</strong> {}%',
            obj.sold_count, obj.reserved_count, obj.available_count, obj.progress_percentage
        )
    progress_display.short_description = 'Estatísticas'
    
    def create_quotas_action(self, request, queryset):
        """Ação para criar cotas para produtos selecionados."""
        created_count = 0
        for product in queryset:
            try:
                quotas_created = create_product_quotas(product.id)
                if quotas_created > 0:
                    created_count += 1
            except Exception as e:
                self.message_user(request, f'Erro ao criar cotas para {product.title}: {str(e)}', level=messages.ERROR)
        
        if created_count > 0:
            self.message_user(request, f'Cotas criadas para {created_count} produto(s).', level=messages.SUCCESS)
    create_quotas_action.short_description = 'Criar cotas para produtos selecionados'
    
    def activate_products(self, request, queryset):
        """Ativa produtos selecionados."""
        updated = queryset.update(status=Product.ACTIVE)
        self.message_user(request, f'{updated} produto(s) ativado(s).', level=messages.SUCCESS)
    activate_products.short_description = 'Ativar produtos selecionados'
    
    def close_products(self, request, queryset):
        """Encerra produtos selecionados."""
        updated = queryset.update(status=Product.CLOSED)
        self.message_user(request, f'{updated} produto(s) encerrado(s).', level=messages.SUCCESS)
    close_products.short_description = 'Encerrar produtos selecionados'


class QuotaInlineOrder(admin.TabularInline):
    """Inline para exibir cotas no admin de pedidos."""
    model = Quota
    extra = 0
    readonly_fields = ('number', 'product', 'status', 'reserved_until')
    fields = ('number', 'product', 'status', 'reserved_until')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin para pedidos."""
    
    list_display = (
        'id', 'full_name', 'product_link', 'quantity', 'total_price_display',
        'status_badge', 'contact_info', 'reserve_expires_at', 'created_at'
    )
    list_filter = ('status', 'product', 'created_at')
    search_fields = ('full_name', 'email', 'whatsapp', 'id')
    readonly_fields = ('total_price_cents', 'created_at', 'updated_at', 'quotas_display')
    fieldsets = (
        ('Informações do Pedido', {
            'fields': ('product', 'quantity', 'total_price_cents', 'status')
        }),
        ('Dados do Cliente', {
            'fields': ('full_name', 'email', 'whatsapp')
        }),
        ('Pagamento', {
            'fields': ('receipt', 'reserve_expires_at')
        }),
        ('Cotas', {
            'fields': ('quotas_display',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [QuotaInlineOrder]
    actions = ['confirm_orders', 'cancel_orders', 'mark_as_expired']
    
    def product_link(self, obj):
        """Link para o produto."""
        url = reverse('admin:raffles_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.title)
    product_link.short_description = 'Produto'
    product_link.admin_order_field = 'product__title'
    
    def total_price_display(self, obj):
        """Preço total formatado."""
        return obj.total_price_display
    total_price_display.short_description = 'Valor Total'
    total_price_display.admin_order_field = 'total_price_cents'
    
    def status_badge(self, obj):
        """Status com badge colorido."""
        colors = {
            'reservado': 'warning',
            'aguardando_comprovante': 'info',
            'aguardando_confirmacao': 'primary',
            'confirmado': 'success',
            'cancelado': 'danger',
            'expirado': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def contact_info(self, obj):
        """Informações de contato."""
        contacts = []
        if obj.email:
            contacts.append(format_html('<i class="fa fa-envelope"></i> {}', obj.email))
        if obj.whatsapp:
            contacts.append(format_html('<i class="fa fa-whatsapp"></i> {}', obj.whatsapp))
        return format_html('<br>'.join(contacts)) if contacts else '-'
    contact_info.short_description = 'Contato'
    
    def quotas_display(self, obj):
        """Exibe as cotas do pedido."""
        quotas = obj.quotas.all().order_by('number')
        if quotas.exists():
            numbers = [str(q.number) for q in quotas]
            return format_html(
                '<strong>Números das cotas:</strong><br>{}',
                ', '.join(numbers)
            )
        return 'Nenhuma cota encontrada'
    quotas_display.short_description = 'Cotas'
    
    def confirm_orders(self, request, queryset):
        """Confirma pedidos selecionados."""
        confirmed_count = 0
        for order in queryset:
            try:
                if confirm_order(order.id, admin_user=request.user):
                    confirmed_count += 1
            except Exception as e:
                self.message_user(request, f'Erro ao confirmar pedido #{order.id}: {str(e)}', level=messages.ERROR)
        
        if confirmed_count > 0:
            self.message_user(request, f'{confirmed_count} pedido(s) confirmado(s).', level=messages.SUCCESS)
    confirm_orders.short_description = 'Confirmar pedidos selecionados'
    
    def cancel_orders(self, request, queryset):
        """Cancela pedidos selecionados."""
        canceled_count = 0
        for order in queryset:
            try:
                if cancel_order(order.id, admin_user=request.user):
                    canceled_count += 1
            except Exception as e:
                self.message_user(request, f'Erro ao cancelar pedido #{order.id}: {str(e)}', level=messages.ERROR)
        
        if canceled_count > 0:
            self.message_user(request, f'{canceled_count} pedido(s) cancelado(s).', level=messages.SUCCESS)
    cancel_orders.short_description = 'Cancelar pedidos selecionados'
    
    def mark_as_expired(self, request, queryset):
        """Marca pedidos como expirados."""
        now = timezone.now()
        expired_count = queryset.filter(
            status__in=['reservado', 'aguardando_confirmacao'],
            reserve_expires_at__lt=now
        ).update(status='expirado')
        
        if expired_count > 0:
            self.message_user(request, f'{expired_count} pedido(s) marcado(s) como expirado(s).', level=messages.SUCCESS)
        else:
            self.message_user(request, 'Nenhum pedido elegível para expiração encontrado.', level=messages.WARNING)
    mark_as_expired.short_description = 'Marcar como expirados'


@admin.register(Quota)
class QuotaAdmin(admin.ModelAdmin):
    """Admin para cotas."""
    
    list_display = ('product_link', 'number', 'status_badge', 'order_link', 'reserved_until')
    list_filter = ('product', 'status', 'reserved_until')
    search_fields = ('number', 'product__title', 'order__full_name')
    readonly_fields = ('product', 'number')
    
    def product_link(self, obj):
        """Link para o produto."""
        url = reverse('admin:raffles_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.title)
    product_link.short_description = 'Produto'
    product_link.admin_order_field = 'product__title'
    
    def order_link(self, obj):
        """Link para o pedido."""
        if obj.order:
            url = reverse('admin:raffles_order_change', args=[obj.order.id])
            return format_html('<a href="{}">Pedido #{}</a>', url, obj.order.id)
        return '-'
    order_link.short_description = 'Pedido'
    order_link.admin_order_field = 'order__id'
    
    def status_badge(self, obj):
        """Status com badge colorido."""
        colors = {
            'disponivel': 'success',
            'reservada': 'warning',
            'vendida': 'primary'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    """Admin para logs administrativos."""
    
    list_display = ('action', 'admin_id', 'created_at', 'details_preview')
    list_filter = ('action', 'created_at')
    search_fields = ('action', 'admin_id', 'details')
    readonly_fields = ('admin_id', 'action', 'details', 'created_at')
    
    def details_preview(self, obj):
        """Preview dos detalhes do log."""
        if obj.details:
            details_str = str(obj.details)[:100]
            if len(str(obj.details)) > 100:
                details_str += '...'
            return details_str
        return '-'
    details_preview.short_description = 'Detalhes'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Configurações do Admin Site
admin.site.site_header = "Sistema de Cotas - Administração"
admin.site.site_title = "Sistema de Cotas"
admin.site.index_title = "Painel Administrativo"
