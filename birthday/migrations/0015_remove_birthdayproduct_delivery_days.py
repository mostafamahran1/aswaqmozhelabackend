from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('birthday', '0014_birthdayproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='birthdayproduct',
            name='delivery_days',
        ),
    ]
