# Generated by Django 5.0.1 on 2024-12-10 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socks', '0004_socksproduct_model_name_alter_socksproduct_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='socksproduct',
            name='category',
        ),
    ]
