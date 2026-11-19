from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phones', '0016_phonesproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='phonesproduct',
            name='delivery_days',
        ),
    ]
