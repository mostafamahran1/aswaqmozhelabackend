# Generated by Django 5.0.1 on 2024-07-18 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonesproduct',
            name='delivery_days',
            field=models.IntegerField(default=3),
        ),
    ]
