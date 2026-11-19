from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0015_couponusage'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_fee',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='standard_delivery_fee',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='free_delivery',
            field=models.BooleanField(default=False),
        ),
    ]
