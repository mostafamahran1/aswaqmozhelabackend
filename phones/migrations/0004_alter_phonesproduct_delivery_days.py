# Generated by Django 5.0.1 on 2024-12-09 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phones', '0003_alter_phonesreview_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonesproduct',
            name='delivery_days',
            field=models.IntegerField(default=1),
        ),
    ]
