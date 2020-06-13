from rest_framework import viewsets

from . import models, serializers


class ClassViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Class.objects.all().order_by('-semester')
    serializer_class = serializers.ClassSerializer
    filterset_fields = {
        'name': ['exact', 'contains'],
        'semester': ['exact'],
        'absences': ['exact', 'gt', 'gte', 'lt', 'lte'],
        'grade': ['exact', 'gt', 'gte', 'lt', 'lte'],
        'updated': ['gt', 'gte', 'lt', 'lte'],
    }
