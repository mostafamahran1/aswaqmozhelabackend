from django.contrib import admin
from .models import SocksProduct

@admin.register(SocksProduct)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'createAT', 'user')
    search_fields = ('name', 'description')
    list_filter = ('createAT', 'user')
