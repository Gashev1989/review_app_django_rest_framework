import django_filters as filters

from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """Фильтрация для названия произведения."""
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='contains'
    )
    year = filters.NumberFilter(
        field_name='year',
        lookup_expr='exact'
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='exact'
    )
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )

    class Meta:
        model = Title
        fields = ['name', 'year', 'genre', 'category']
