from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spices', '0015_spicesproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spicesproduct',
            name='delivery_days',
        ),
    ]
