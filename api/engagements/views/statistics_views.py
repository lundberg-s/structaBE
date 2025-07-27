from rest_framework import generics, permissions
from rest_framework.response import Response
from engagements.statistics.main import get_all_work_item_statistics
from engagements.models import WorkItem, Comment
from core.models import AuditLog
from core.views.base_views import BaseView


class WorkItemStatisticsView(BaseView, generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tenant = self.get_tenant()
        stats = get_all_work_item_statistics(tenant, Comment, AuditLog, WorkItem)
        return Response(stats) 