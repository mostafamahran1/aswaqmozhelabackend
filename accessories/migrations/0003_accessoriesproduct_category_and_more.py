# Generated by Django 5.0.1 on 2024-12-09 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accessories', '0002_alter_accessoriesproduct_delivery_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessoriesproduct',
            name='category',
            field=models.CharField(choices=[('Phones', 'Phones'), ('Clothes', 'Clothes'), ('Foods', 'Foods'), ('Fav', 'Fav'), ('Pharmacy', 'Pharmacy'), ('Spices', 'Spices'), ('Supermarket', 'Supermarket'), ('Toys', 'Toys')], default='Supermarket', max_length=50),
        ),
        migrations.AlterField(
            model_name='accessoriesproduct',
            name='delivery_days',
            field=models.IntegerField(default=3),
        ),
    ]
