# Generated by Django 5.0.1 on 2024-12-09 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socksproduct',
            name='delivery_days',
            field=models.IntegerField(default=1),
        ),
    ]
