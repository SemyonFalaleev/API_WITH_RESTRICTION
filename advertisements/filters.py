from django_filters import rest_framework as filters

from advertisements.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""
    created_at = filters.DateFromToRangeFilter()
    status = filters.ChoiceFilter(
        choices=Advertisement._meta.get_field('status').choices
        )
    creator = filters.NumberFilter(field_name="creator")
    class Meta:
        model = Advertisement
        fields = ['status', 'created_at', 'creator']
