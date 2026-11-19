from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0015_foodsproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodsproduct',
            name='delivery_days',
        ),
    ]
