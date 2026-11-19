from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gifts', '0014_giftsproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='giftsproduct',
            name='delivery_days',
        ),
    ]
