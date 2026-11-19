from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_libraryproduct_orders_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='libraryproduct',
            name='delivery_days',
        ),
    ]
