from django.contrib import admin
from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # عرض ID واسم الفئة في لوحة الإدارة
    ordering = ('id',)  # ترتيب القائمة حسب ID
    search_fields = ('name',)  # إمكانية البحث عن طريق الاسم

admin.site.register(Category, CategoryAdmin)
