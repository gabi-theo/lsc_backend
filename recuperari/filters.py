import django_filters

from .models import Session


class SessionFilter(django_filters.FilterSet):
    class Meta:
        model = Session
        fields = ['date']
