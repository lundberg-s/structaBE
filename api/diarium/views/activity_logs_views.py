from rest_framework import generics, permissions
from diarium.models import ActivityLog
from diarium.serializers import ActivityLogSerializer

class ActivityLogListCreateView(generics.ListCreateAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = ActivityLog.objects.select_related('user', 'case').all()
        case_id = self.request.query_params.get('caseId')
        if case_id:
            queryset = queryset.filter(case__id=case_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ActivityLogRetrieveView(generics.RetrieveAPIView):
    queryset = ActivityLog.objects.select_related('user', 'case').all()
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id' 