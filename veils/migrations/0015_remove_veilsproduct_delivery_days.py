from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('veils', '0014_veilsproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='veilsproduct',
            name='delivery_days',
        ),
    ]
