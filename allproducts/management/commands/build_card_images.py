from django.core.management.base import BaseCommand

from allproducts.views import MODEL_MAPPING
from utils.images import _write_card_image


class Command(BaseCommand):
    help = 'Build the small card WebP for every product that does not have one yet.'

    def handle(self, *args, **options):
        built = 0
        skipped = 0
        for model in MODEL_MAPPING.values():
            products = model.objects.exclude(primary_image='').exclude(primary_image__isnull=True).iterator()
            for product in products:
                if not product.primary_image:
                    skipped += 1
                    continue
                try:
                    name = _write_card_image(product.primary_image, force=False)
                except Exception as exc:
                    name = None
                    if skipped < 3:
                        self.stderr.write(f'{model.__name__} {product.id}: {exc}')
                if name:
                    built += 1
                else:
                    skipped += 1
                if built and built % 25 == 0:
                    self.stdout.write(f'cards ready: {built}')
        self.stdout.write(self.style.SUCCESS(f'card images checked. ready={built} skipped={skipped}'))
