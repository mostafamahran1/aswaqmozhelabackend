from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class InboxNotice(models.Model):
    audience = models.CharField(max_length=20)
    title = models.CharField(max_length=120)
    body = models.TextField()
    kind = models.CharField(max_length=30, default='announcement')
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['audience', 'created_at']),
        ]


class NoticeRead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notice_reads')
    notice = models.ForeignKey(InboxNotice, on_delete=models.CASCADE, related_name='reads')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'notice'], name='unique_notice_read'),
        ]


class AppRelease(models.Model):
    version_name = models.CharField(max_length=20)
    build_number = models.PositiveIntegerField()
    title = models.CharField(max_length=120, default='تحديث جديد')
    message = models.TextField(
        default='في تحديث جديد للتطبيق. نزّله دلوقتي عشان تستخدم آخر نسخة.',
    )
    store_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-build_number', '-created_at']

    def __str__(self):
        return f'{self.version_name} ({self.build_number})'


class CustomerPresence(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='presence')
    last_notified = models.DateTimeField(null=True, blank=True)

    def should_notify(self):
        if self.last_notified is None:
            return True
        return timezone.now() - self.last_notified >= timedelta(hours=6)

    def mark_notified(self):
        self.last_notified = timezone.now()
        self.save(update_fields=['last_notified'])
