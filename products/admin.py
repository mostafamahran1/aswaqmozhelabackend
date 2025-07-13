from django.contrib import admin
from .models import LibraryProduct

@admin.register(LibraryProduct)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price','original_price', 'discount_percentage', 'stock', 'createAT', 'user')
    search_fields = ('name', 'description')
    list_filter = ('createAT', 'user')

