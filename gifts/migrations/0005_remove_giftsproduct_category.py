# Generated by Django 5.0.1 on 2024-12-10 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gifts', '0004_giftsproduct_model_name_alter_giftsproduct_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='giftsproduct',
            name='category',
        ),
    ]