from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socks', '0014_socksproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='socksproduct',
            name='delivery_days',
        ),
    ]
