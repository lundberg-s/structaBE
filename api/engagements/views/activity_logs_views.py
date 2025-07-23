from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import ValidationError

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters

from engagements.models import ActivityLog
from engagements.serializers.activity_log_serializers import ActivityLogSerializer


class ActivityLogListView(generics.ListCreateAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["work_item", "user", "activity_type"]
    search_fields = ["description"]

    def get_queryset(self):
        base_queryset = ActivityLog.objects.filter(tenant=self.request.user.tenant)
        return self.get_serializer_class().get_optimized_queryset(base_queryset)

    def filter_queryset(self, queryset):
        try:
            return super().filter_queryset(queryset)
        except ValidationError:
            # If filters are invalid (e.g. bad UUID), return empty queryset with 200
            return queryset.none()

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant, user=self.request.user)


class ActivityLogDetailView(generics.RetrieveAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    
    def get_queryset(self):
        base_queryset = ActivityLog.objects.filter(tenant=self.request.user.tenant)
        return self.get_serializer_class().get_optimized_queryset(base_queryset)
