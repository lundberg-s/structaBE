from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import ValidationError

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters

from diarium.models import ActivityLog
from diarium.serializers import ActivityLogSerializer

class ActivityLogListCreateView(generics.ListCreateAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['case', 'user', 'activity_type']
    search_fields = ['description']

    def get_queryset(self):
        return ActivityLog.objects.select_related('user', 'case').all()

    def filter_queryset(self, queryset):
        try:
            return super().filter_queryset(queryset)
        except ValidationError:
            # If filters are invalid (e.g. bad UUID), return empty queryset with 200
            return queryset.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ActivityLogRetrieveView(generics.RetrieveAPIView):
    queryset = ActivityLog.objects.select_related('user', 'case').all()
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id' 