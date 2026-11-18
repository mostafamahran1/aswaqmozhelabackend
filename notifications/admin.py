from django.contrib import admin

from .models import CustomerPresence, InboxNotice, NoticeRead

admin.site.register(CustomerPresence)
admin.site.register(InboxNotice)
admin.site.register(NoticeRead)
