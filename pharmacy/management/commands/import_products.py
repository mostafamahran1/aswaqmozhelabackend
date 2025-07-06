from django.core.management.base import BaseCommand
import csv
import requests
from io import BytesIO
from django.core.files import File
from pharmacy.models import PharmacyProduct
from supermarket.models import SupermarketProduct
from shein.models import SheinProduct
from django.contrib.auth.models import User

MODEL_MAP = {
    'Pharmacy': PharmacyProduct,
    'Supermarket': SupermarketProduct,
    'Clothes' : SheinProduct
}

def import_products_from_csv(csv_path, default_user_id):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        user = User.objects.get(id=default_user_id)

        for row in reader:
            model = MODEL_MAP.get(row['model_name'])
            if not model:
                print(f"Skipping unknown model_name: {row['model_name']}")
                continue

            image_file = None
            if row['image_url']:
                response = requests.get(row['image_url'])
                if response.status_code == 200:
                    image_file = File(BytesIO(response.content), name=f"{row['name'].replace(' ', '_')}.jpg")

            product = model.objects.create(
                name=row['name'],
                model_name=row['model_name'],
                price=float(row['price']),
                description=row['description'],
                stock=int(row['stock']),
                delivery_days=int(row['delivery_days']),
                is_active=row['is_active'].lower() == 'true',
                is_available=row['is_available'].lower() == 'true',
                user=user,
            )

            if image_file:
                product.primary_image.save(image_file.name, image_file, save=True)

            print(f"✅ Imported: {product.name}")

class Command(BaseCommand):
    help = 'Import products from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str)
        parser.add_argument('user_id', type=int)

    def handle(self, *args, **kwargs):
        csv_path = kwargs['csv_path']
        user_id = kwargs['user_id']
        import_products_from_csv(csv_path, user_id)
