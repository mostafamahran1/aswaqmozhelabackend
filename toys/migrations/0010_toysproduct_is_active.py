# Generated by Django 5.0.1 on 2024-12-17 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toys', '0009_alter_toysproduct_delivery_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='toysproduct',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
