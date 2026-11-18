import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0015_couponusage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=50)),
                ('product_id', models.PositiveIntegerField()),
                ('rating', models.PositiveSmallIntegerField()),
                ('comment', models.CharField(blank=True, default='', max_length=500)),
                ('verified_purchase', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AppFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField()),
                ('suggestion', models.CharField(blank=True, default='', max_length=800)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='app_feedback', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='productreview',
            index=models.Index(fields=['model_name', 'product_id', '-created_at'], name='reviews_prod_lookup_idx'),
        ),
        migrations.AddConstraint(
            model_name='productreview',
            constraint=models.UniqueConstraint(fields=('user', 'model_name', 'product_id'), name='one_review_per_product'),
        ),
        migrations.AddConstraint(
            model_name='appfeedback',
            constraint=models.UniqueConstraint(condition=models.Q(('order__isnull', False)), fields=('user', 'order'), name='one_feedback_per_order'),
        ),
    ]
