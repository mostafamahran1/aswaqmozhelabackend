# Generated by Django 5.0.1 on 2024-12-17 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veils', '0007_alter_veilsproduct_model_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='veilsproduct',
            name='delivery_days',
            field=models.IntegerField(default=1),
        ),
    ]