# Generated by Django 5.0.1 on 2024-10-17 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offerspaner', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('image1', models.ImageField(upload_to='uploads/')),
                ('image2', models.ImageField(upload_to='uploads/')),
                ('image3', models.ImageField(upload_to='uploads/')),
            ],
        ),
        migrations.DeleteModel(
            name='AdImage',
        ),
    ]
