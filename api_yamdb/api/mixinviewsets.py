from rest_framework import filters, mixins, viewsets

from .permissions import IsAdmin


class CreateListDestroyMixins(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    """Миксин-вьюсет для категорий и жанров произведений."""
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
