# Generated by Django 5.0.1 on 2025-07-06 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('birthday', '0011_alter_birthdayproduct_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='birthdayproduct',
            name='model_name',
            field=models.CharField(choices=[('Phones', 'Phones'), ('Shein', 'Shein'), ('Foods', 'Foods'), ('Fav', 'Fav'), ('Pharmacy', 'Pharmacy'), ('Spices', 'Spices'), ('Supermarket', 'Supermarket'), ('Toys', 'Toys'), ('Veils', 'Veils'), ('Socks', 'Socks'), ('Birthday', 'Birthday'), ('Gifts', 'Gifts'), ('Accessories', 'Accessories'), ('Library', 'Library')], default='Supermarket', max_length=50),
        ),
    ]
