# Generated by Django 5.0.1 on 2024-12-10 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toys', '0005_toysproduct_model_name_alter_toysproduct_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='toysproduct',
            name='category',
        ),
    ]
