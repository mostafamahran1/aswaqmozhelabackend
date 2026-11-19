from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_inbox'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppRelease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_name', models.CharField(max_length=20)),
                ('build_number', models.PositiveIntegerField()),
                ('title', models.CharField(default='تحديث جديد', max_length=120)),
                ('message', models.TextField(default='في تحديث جديد للتطبيق. نزّله دلوقتي عشان تستخدم آخر نسخة.')),
                ('store_url', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-build_number', '-created_at'],
            },
        ),
    ]
