# Generated by Django 5.0.1 on 2024-12-17 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('birthday', '0008_alter_birthdayproduct_delivery_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='birthdayproduct',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
