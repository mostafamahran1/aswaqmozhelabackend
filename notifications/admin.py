from django.contrib import admin

from .models import AppRelease, CustomerPresence, InboxNotice, NoticeRead

admin.site.register(CustomerPresence)
admin.site.register(InboxNotice)
admin.site.register(NoticeRead)


@admin.register(AppRelease)
class AppReleaseAdmin(admin.ModelAdmin):
    list_display = ('version_name', 'build_number', 'title', 'created_at')
    ordering = ('-build_number',)
