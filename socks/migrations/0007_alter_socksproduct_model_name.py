# Generated by Django 5.0.1 on 2024-12-10 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socks', '0006_alter_socksproduct_model_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socksproduct',
            name='model_name',
            field=models.CharField(choices=[('Phones', 'Phones'), ('Clothes', 'Clothes'), ('Foods', 'Foods'), ('Fav', 'Fav'), ('Pharmacy', 'Pharmacy'), ('Spices', 'Spices'), ('Supermarket', 'Supermarket'), ('Toys', 'Toys'), ('Veils', 'Veils'), ('Socks', 'Socks'), ('Birthday', 'Birthday'), ('Gifts', 'Gifts'), ('Accessories', 'Accessories'), ('Library', 'Library')], default='Supermarket', max_length=50),
        ),
    ]
