# Generated by Django 5.0.1 on 2024-12-10 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fruitsandvegetables', '0005_favproduct_model_name_alter_favproduct_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='favproduct',
            name='category',
        ),
    ]
