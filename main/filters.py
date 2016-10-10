from rest_framework import filters
from .models import Product

class ProductFilter(filters.FilterSet):

    #show_expired = django_filters.BooleanFilter(method='show_expired_filter')

    class Meta:
        model = Product
        fields = {
            'price': ['lte', 'gte'],
            'title': ['icontains'],
        }

    #def show_expired_filter(self, queryset, name, value):
    #    if not value:
    #        current_time = now()
    #        queryset = queryset.filter( expire_date__gt=current_time)
    #    return queryset