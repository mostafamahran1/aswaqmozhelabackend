from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supermarket', '0015_supermarketproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supermarketproduct',
            name='delivery_days',
        ),
    ]
