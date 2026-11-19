from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0015_pharmacyproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pharmacyproduct',
            name='delivery_days',
        ),
    ]
