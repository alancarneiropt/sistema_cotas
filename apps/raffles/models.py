"""
Models for the raffles app.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model


class Product(models.Model):
    """Modelo para produtos/sorteios."""
    
    DRAFT = "rascunho"
    ACTIVE = "ativo"
    CLOSED = "encerrado"
    STATUS_CHOICES = [
        (DRAFT, "Rascunho"),
        (ACTIVE, "Ativo"),
        (CLOSED, "Encerrado")
    ]

    title = models.CharField(
        max_length=180,
        verbose_name="Título",
        help_text="Nome do produto/sorteio"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada do produto"
    )
    price_cents = models.PositiveIntegerField(
        verbose_name="Preço por cota (centavos)",
        help_text="Preço por cota em centavos (BRL). Ex: 1000 = R$ 10,00",
        validators=[MinValueValidator(1)]
    )
    total_quotas = models.PositiveIntegerField(
        verbose_name="Total de cotas",
        help_text="Número total de cotas disponíveis",
        validators=[MinValueValidator(1)]
    )
    draw_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data e hora do sorteio",
        help_text="Quando será realizado o sorteio"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT,
        verbose_name="Status"
    )
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name="Imagem do produto"
    )

    # Campos para o resultado do sorteio
    drawn_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número sorteado",
        help_text="Número da cota sorteada"
    )
    draw_source = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Fonte do sorteio",
        help_text="Descrição de como foi realizado o sorteio"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-created_at']

    @property
    def sold_count(self):
        """Retorna o número de cotas vendidas."""
        return Quota.objects.filter(
            product=self,
            status=Quota.SOLD
        ).count()

    @property
    def reserved_count(self):
        """Retorna o número de cotas reservadas."""
        return Quota.objects.filter(
            product=self,
            status=Quota.RESERVED
        ).count()

    @property
    def available_count(self):
        """Retorna o número de cotas disponíveis."""
        return self.total_quotas - self.sold_count - self.reserved_count

    @property
    def progress_percentage(self):
        """Retorna a porcentagem de cotas vendidas."""
        if self.total_quotas == 0:
            return 0
        return round((self.sold_count / self.total_quotas) * 100, 2)

    @property
    def price_display(self):
        """Retorna o preço formatado em reais."""
        return f"R$ {self.price_cents / 100:.2f}".replace('.', ',')

    def __str__(self):
        return self.title


class Order(models.Model):
    """Modelo para pedidos de cotas."""
    
    RESERVED = "reservado"
    WAITING_PROOF = "aguardando_comprovante"
    WAITING_CONFIRM = "aguardando_confirmacao"
    CONFIRMED = "confirmado"
    CANCELED = "cancelado"
    EXPIRED = "expirado"
    
    STATUS_CHOICES = [
        (RESERVED, "Reservado"),
        (WAITING_PROOF, "Aguardando comprovante"),
        (WAITING_CONFIRM, "Aguardando confirmação"),
        (CONFIRMED, "Confirmado"),
        (CANCELED, "Cancelado"),
        (EXPIRED, "Expirado"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Produto"
    )
    full_name = models.CharField(
        max_length=180,
        verbose_name="Nome completo"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="E-mail"
    )
    whatsapp = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="WhatsApp",
        help_text="Formatos +55..., +351..., etc."
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Quantidade de cotas",
        validators=[MinValueValidator(1)]
    )
    total_price_cents = models.PositiveIntegerField(
        verbose_name="Valor total (centavos)"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=RESERVED,
        verbose_name="Status"
    )
    receipt = models.FileField(
        upload_to="receipts/",
        null=True,
        blank=True,
        verbose_name="Comprovante de pagamento"
    )
    reserve_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Reserva expira em"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']

    def contact_provided(self):
        """Verifica se pelo menos um contato foi fornecido."""
        return bool(self.email or self.whatsapp)

    @property
    def total_price_display(self):
        """Retorna o preço total formatado em reais."""
        return f"R$ {self.total_price_cents / 100:.2f}".replace('.', ',')

    @property
    def is_expired(self):
        """Verifica se a reserva expirou."""
        if not self.reserve_expires_at:
            return False
        return timezone.now() > self.reserve_expires_at

    def __str__(self):
        return f"Pedido #{self.pk} - {self.full_name}"


class Quota(models.Model):
    """Modelo para cotas individuais."""
    
    AVAILABLE = "disponivel"
    RESERVED = "reservada"
    SOLD = "vendida"
    
    STATUS_CHOICES = [
        (AVAILABLE, "Disponível"),
        (RESERVED, "Reservada"),
        (SOLD, "Vendida"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Produto"
    )
    number = models.PositiveIntegerField(
        verbose_name="Número da cota"
    )
    order = models.ForeignKey(
        Order,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Pedido"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=AVAILABLE,
        verbose_name="Status"
    )
    reserved_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Reservada até"
    )

    class Meta:
        verbose_name = "Cota"
        verbose_name_plural = "Cotas"
        unique_together = ("product", "number")
        ordering = ['product', 'number']

    @property
    def is_expired(self):
        """Verifica se a reserva expirou."""
        if not self.reserved_until or self.status != self.RESERVED:
            return False
        return timezone.now() > self.reserved_until

    def __str__(self):
        return f"{self.product.title} - Cota {self.number} ({self.status})"


class AdminLog(models.Model):
    """Modelo para log de ações administrativas."""
    
    admin_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="ID do Administrador"
    )
    action = models.CharField(
        max_length=120,
        verbose_name="Ação"
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalhes"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Log Administrativo"
        verbose_name_plural = "Logs Administrativos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
