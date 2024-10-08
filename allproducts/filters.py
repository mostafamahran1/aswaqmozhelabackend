import django_filters
from .models import Allproduct
from django.db.models import Q


class ProductsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', 
        lookup_expr='icontains', 
        label='Product Name'
    )
    min_price = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='gte', 
        label='Minimum Price'
    )
    max_price = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='lte', 
        label='Maximum Price'
    )
    keyword = django_filters.CharFilter(
        method='filter_by_keyword', 
        label='Keyword'
    )

    def filter_by_keyword(self, queryset, name, value):
        """
        Custom filter method to search for the keyword in both name and description fields.
        """
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    class Meta:
        model = Allproduct
        fields = ['name', 'min_price', 'max_price', 'keyword']
