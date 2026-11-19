from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fruitsandvegetables', '0015_favproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='favproduct',
            name='delivery_days',
        ),
    ]
