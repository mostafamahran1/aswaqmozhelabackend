# Generated by Django 5.0.1 on 2024-12-09 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supermarket', '0002_supermarketproduct_delivery_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supermarketproduct',
            name='delivery_days',
            field=models.IntegerField(default=1),
        ),
    ]