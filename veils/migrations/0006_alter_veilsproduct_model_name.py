# Generated by Django 5.0.1 on 2024-12-10 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veils', '0005_remove_veilsproduct_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='veilsproduct',
            name='model_name',
            field=models.CharField(choices=[('Phones', 'Phones'), ('Clothes', 'Clothes'), ('Foods', 'Foods'), ('Fav', 'Fav'), ('Pharmacy', 'Pharmacy'), ('Spices', 'Spices'), ('Supermarket', 'Supermarket'), ('Toys', 'Toys'), ('Veils', 'Veils'), ('Socks', 'Socks'), ('Birthday', 'Birthday'), ('Gifts', 'Gifts'), ('Accessories', 'Accessories')], default='Supermarket', max_length=50),
        ),
    ]
