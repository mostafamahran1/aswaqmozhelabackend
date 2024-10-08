from django.contrib import admin
from .models import PharmacyProduct

@admin.register(PharmacyProduct)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'createAT', 'user')
    search_fields = ('name', 'description')
    list_filter = ('createAT', 'user')

