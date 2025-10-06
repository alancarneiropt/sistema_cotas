"""
Formulários para a app raffles.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Order


class PublicOrderForm(forms.Form):
    """Formulário público para pedidos de cotas."""
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(status=Product.ACTIVE),
        empty_label="Selecione um produto",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label="Produto"
    )
    
    full_name = forms.CharField(
        min_length=5,
        max_length=180,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome completo',
            'required': True
        }),
        label="Nome completo"
    )
    
    quantity = forms.IntegerField(
        min_value=1,
        max_value=100,  # Limite para evitar pedidos muito grandes
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Quantidade de cotas',
            'required': True
        }),
        label="Quantidade de cotas"
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com (opcional)'
        }),
        label="E-mail"
    )
    
    whatsapp = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+55 11 99999-9999 (opcional)'
        }),
        label="WhatsApp"
    )
    
    receipt = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        label="Comprovante de pagamento (opcional)",
        help_text="Formatos aceitos: PDF, JPG, PNG (máximo 10MB)"
    )

    def clean(self):
        """Validações personalizadas do formulário."""
        cleaned_data = super().clean()
        
        # Verifica se pelo menos um contato foi fornecido
        email = cleaned_data.get("email")
        whatsapp = cleaned_data.get("whatsapp")
        
        if not email and not whatsapp:
            raise ValidationError(
                "Você deve informar pelo menos um contato (e-mail ou WhatsApp)."
            )
        
        # Valida WhatsApp se fornecido
        if whatsapp:
            whatsapp_clean = whatsapp.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not whatsapp_clean.startswith("+"):
                raise ValidationError(
                    "WhatsApp deve começar com + seguido do código do país."
                )
        
        # Verifica disponibilidade de cotas
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")
        
        if product and quantity:
            available_count = product.available_count
            if quantity > available_count:
                raise ValidationError(
                    f"Quantidade solicitada ({quantity}) é maior que "
                    f"cotas disponíveis ({available_count})."
                )
        
        return cleaned_data

    def clean_receipt(self):
        """Validação do arquivo de comprovante."""
        receipt = self.cleaned_data.get('receipt')
        
        if receipt:
            # Verifica tamanho do arquivo (10MB)
            max_size = 10 * 1024 * 1024  # 10MB em bytes
            if receipt.size > max_size:
                raise ValidationError(
                    "Arquivo muito grande. Tamanho máximo permitido: 10MB"
                )
            
            # Verifica tipo de arquivo
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            file_extension = receipt.name.lower().split('.')[-1]
            
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError(
                    "Tipo de arquivo não permitido. "
                    "Use apenas PDF, JPG ou PNG."
                )
        
        return receipt


class ReceiptUploadForm(forms.Form):
    """Formulário para upload de comprovante após o pedido."""
    
    order_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    
    receipt = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        label="Comprovante de pagamento",
        help_text="Formatos aceitos: PDF, JPG, PNG (máximo 10MB)"
    )

    def clean_receipt(self):
        """Validação do arquivo de comprovante."""
        receipt = self.cleaned_data.get('receipt')
        
        if not receipt:
            raise ValidationError("Selecione um arquivo de comprovante.")
        
        # Verifica tamanho do arquivo (10MB)
        max_size = 10 * 1024 * 1024  # 10MB em bytes
        if receipt.size > max_size:
            raise ValidationError(
                "Arquivo muito grande. Tamanho máximo permitido: 10MB"
            )
        
        # Verifica tipo de arquivo
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_extension = receipt.name.lower().split('.')[-1]
        
        if f'.{file_extension}' not in allowed_extensions:
            raise ValidationError(
                "Tipo de arquivo não permitido. "
                "Use apenas PDF, JPG ou PNG."
            )
        
        return receipt

    def clean_order_id(self):
        """Valida se o pedido existe e pode receber comprovante."""
        order_id = self.cleaned_data.get('order_id')
        
        try:
            order = Order.objects.get(id=order_id)
            
            if order.status not in [Order.RESERVED, Order.WAITING_CONFIRM]:
                raise ValidationError(
                    "Este pedido não pode receber comprovante no momento."
                )
            
            if order.is_expired:
                raise ValidationError("Pedido expirado.")
                
        except Order.DoesNotExist:
            raise ValidationError("Pedido não encontrado.")
        
        return order_id


class ProductForm(forms.ModelForm):
    """Formulário para criação/edição de produtos (admin)."""
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price_cents', 'total_quotas',
            'draw_datetime', 'status', 'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'price_cents': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'total_quotas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'draw_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_price_cents(self):
        """Validação do preço."""
        price_cents = self.cleaned_data.get('price_cents')
        
        if price_cents <= 0:
            raise ValidationError("Preço deve ser maior que zero.")
        
        return price_cents

    def clean_total_quotas(self):
        """Validação do total de cotas."""
        total_quotas = self.cleaned_data.get('total_quotas')
        
        if total_quotas <= 0:
            raise ValidationError("Total de cotas deve ser maior que zero.")
        
        # Se é um produto existente e tem cotas vendidas, não permite diminuir
        if self.instance.pk:
            sold_count = self.instance.sold_count
            if total_quotas < sold_count:
                raise ValidationError(
                    f"Não é possível ter menos cotas ({total_quotas}) "
                    f"que já foram vendidas ({sold_count})."
                )
        
        return total_quotas


class OrderStatusForm(forms.ModelForm):
    """Formulário para alteração de status de pedidos (admin)."""
    
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define as opções de status baseado no status atual
        current_status = self.instance.status if self.instance.pk else None
        
        status_choices = []
        
        if current_status == Order.RESERVED:
            status_choices = [
                (Order.WAITING_CONFIRM, "Aguardando confirmação"),
                (Order.CONFIRMED, "Confirmado"),
                (Order.CANCELED, "Cancelado"),
            ]
        elif current_status == Order.WAITING_CONFIRM:
            status_choices = [
                (Order.CONFIRMED, "Confirmado"),
                (Order.CANCELED, "Cancelado"),
            ]
        elif current_status == Order.WAITING_PROOF:
            status_choices = [
                (Order.WAITING_CONFIRM, "Aguardando confirmação"),
                (Order.CONFIRMED, "Confirmado"),
                (Order.CANCELED, "Cancelado"),
            ]
        elif current_status == Order.CONFIRMED:
            status_choices = [
                (Order.CANCELED, "Cancelado"),
            ]
        elif current_status == Order.CANCELED:
            status_choices = [
                (Order.WAITING_CONFIRM, "Aguardando confirmação"),
            ]
        
        self.fields['status'].choices = status_choices


class ProductForm(forms.ModelForm):
    """Formulário para criação/edição de produtos."""
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price_cents', 'total_quotas', 
            'status', 'draw_datetime', 'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do produto'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição do produto'
            }),
            'price_cents': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1',
                'placeholder': 'Preço em centavos (ex: 20 para R$ 0,20)'
            }),
            'total_quotas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1',
                'placeholder': 'Número total de cotas'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'draw_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def clean_price_cents(self):
        price_cents = self.cleaned_data.get('price_cents')
        if price_cents and price_cents <= 0:
            raise ValidationError('O preço deve ser maior que zero.')
        return price_cents
    
    def clean_total_quotas(self):
        total_quotas = self.cleaned_data.get('total_quotas')
        if total_quotas and total_quotas <= 0:
            raise ValidationError('O número de cotas deve ser maior que zero.')
        return total_quotas
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Verifica se o produto já foi sorteado
        if self.instance and self.instance.drawn_number is not None:
            raise ValidationError(
                'Não é possível editar um produto que já foi sorteado. '
                'O produto está marcado como encerrado.'
            )
        
        return cleaned_data
