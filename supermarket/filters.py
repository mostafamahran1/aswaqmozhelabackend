import django_filters
from .models import SupermarketProduct

class ProductsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', field_name='name')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    keyword = django_filters.CharFilter(lookup_expr='icontains', method='filter_by_keyword')

    def filter_by_keyword(self, queryset, name, value):
        return queryset.filter(name__icontains=value) | queryset.filter(description__icontains=value)

    class Meta:
        model = SupermarketProduct
        fields = ['name', 'min_price', 'max_price', 'keyword']
