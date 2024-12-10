# Generated by Django 5.0.1 on 2024-12-09 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phones', '0004_alter_phonesproduct_delivery_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonesproduct',
            name='category',
            field=models.CharField(choices=[('Phones', 'Phones'), ('Clothes', 'Clothes'), ('Foods', 'Foods'), ('Fav', 'Fav'), ('Pharmacy', 'Pharmacy'), ('Spices', 'Spices'), ('Supermarket', 'Supermarket'), ('Toys', 'Toys')], default='Supermarket', max_length=50),
        ),
        migrations.AlterField(
            model_name='phonesproduct',
            name='delivery_days',
            field=models.IntegerField(default=3),
        ),
    ]
