from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InboxNotice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audience', models.CharField(max_length=20)),
                ('title', models.CharField(max_length=120)),
                ('body', models.TextField()),
                ('kind', models.CharField(default='announcement', max_length=30)),
                ('payload', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NoticeRead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read_at', models.DateTimeField(auto_now_add=True)),
                ('notice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reads', to='notifications.inboxnotice')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notice_reads', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='inboxnotice',
            index=models.Index(fields=['audience', 'created_at'], name='notificatio_audienc_8a0f0d_idx'),
        ),
        migrations.AddConstraint(
            model_name='noticeread',
            constraint=models.UniqueConstraint(fields=('user', 'notice'), name='unique_notice_read'),
        ),
    ]
