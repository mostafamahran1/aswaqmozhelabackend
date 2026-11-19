from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0016_order_free_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='expected_delivery_start',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='expected_delivery_end',
            field=models.DateField(blank=True, null=True),
        ),
    ]
