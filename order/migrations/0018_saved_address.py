from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0017_order_delivery_window'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(default='البيت', max_length=40)),
                ('phone_no', models.CharField(max_length=20)),
                ('governorate', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=200)),
                ('street', models.CharField(max_length=500)),
                ('country', models.CharField(default='مصر', max_length=100)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-is_default', '-created_at'],
                'constraints': [
                    models.UniqueConstraint(condition=models.Q(is_default=True), fields=('user',), name='one_default_address_per_user'),
                ],
            },
        ),
    ]
