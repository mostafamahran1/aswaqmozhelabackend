from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toys', '0015_toysproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='toysproduct',
            name='delivery_days',
        ),
    ]
