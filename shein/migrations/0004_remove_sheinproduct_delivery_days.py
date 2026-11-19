from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shein', '0003_sheinproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sheinproduct',
            name='delivery_days',
        ),
    ]
