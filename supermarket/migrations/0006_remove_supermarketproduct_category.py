# Generated by Django 5.0.1 on 2024-12-10 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supermarket', '0005_supermarketproduct_model_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supermarketproduct',
            name='category',
        ),
    ]
