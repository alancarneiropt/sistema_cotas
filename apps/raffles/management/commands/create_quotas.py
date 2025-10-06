"""
Management command para criar cotas para produtos.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import logging

from apps.raffles.models import Product, Quota
from apps.raffles.services import create_product_quotas

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Cria cotas para produtos que ainda não possuem."

    def add_arguments(self, parser):
        parser.add_argument(
            'product_ids',
            nargs='*',
            type=int,
            help='IDs dos produtos para criar cotas (opcional)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Cria cotas para todos os produtos que não possuem',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a execução sem fazer alterações no banco de dados',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação mesmo se já existirem cotas',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        product_ids = options['product_ids']
        all_products = options['all']
        
        self.stdout.write(
            self.style.SUCCESS('=== CRIADOR DE COTAS ===')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO SIMULAÇÃO - Nenhuma alteração será feita')
            )
        
        # Determina quais produtos processar
        if all_products:
            products = Product.objects.all()
            self.stdout.write('Processando todos os produtos...')
        elif product_ids:
            products = Product.objects.filter(id__in=product_ids)
            if not products.exists():
                raise CommandError('Nenhum produto encontrado com os IDs fornecidos.')
        else:
            raise CommandError(
                'Especifique IDs de produtos ou use --all para processar todos.'
            )
        
        total_processed = 0
        total_quotas_created = 0
        
        for product in products:
            try:
                self.stdout.write(f'\nProcessando: {product.title}')
                
                # Verifica se já existem cotas
                existing_quotas = Quota.objects.filter(product=product).count()
                
                if existing_quotas > 0 and not force:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ Produto já possui {existing_quotas} cotas. '
                            'Use --force para recriar.'
                        )
                    )
                    continue
                
                if existing_quotas > 0 and force:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ Produto possui {existing_quotas} cotas. '
                            'Recriando todas as cotas...'
                        )
                    )
                    if not dry_run:
                        Quota.objects.filter(product=product).delete()
                
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
                
                if dry_run:
                    self.stdout.write(
                        f'  ✓ Simulação: {len(quotas_to_create)} cotas seriam criadas'
                    )
                else:
                    with transaction.atomic():
                        Quota.objects.bulk_create(quotas_to_create)
                        
                        logger.info(
                            f'Criadas {len(quotas_to_create)} cotas para o produto {product.title}'
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ {len(quotas_to_create)} cotas criadas para "{product.title}"'
                    )
                )
                
                total_processed += 1
                total_quotas_created += len(quotas_to_create)
                
            except Exception as e:
                logger.error(f'Erro ao criar cotas para produto {product.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Erro ao processar "{product.title}": {str(e)}'
                    )
                )
        
        # Resumo final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Resumo da operação:')
        )
        self.stdout.write(f'  Produtos processados: {total_processed}')
        self.stdout.write(f'  Total de cotas criadas: {total_quotas_created}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Simulação concluída. Use sem --dry-run para executar.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Operação concluída com sucesso!')
            )
