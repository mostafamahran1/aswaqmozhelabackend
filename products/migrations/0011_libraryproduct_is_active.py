# Generated by Django 5.0.1 on 2024-12-17 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_alter_libraryproduct_delivery_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryproduct',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
