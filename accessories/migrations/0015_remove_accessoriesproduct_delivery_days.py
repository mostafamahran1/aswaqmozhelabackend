from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accessories', '0014_accessoriesproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accessoriesproduct',
            name='delivery_days',
        ),
    ]
