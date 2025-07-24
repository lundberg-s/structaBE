from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from engagements.statistics import get_all_work_item_statistics
from engagements.models import WorkItem, ActivityLog, Comment
from core.views.base_views import BaseView

class WorkItemStatisticsView(BaseView, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = self.get_tenant()
        stats = get_all_work_item_statistics(tenant, Comment, ActivityLog, WorkItem)
        return Response(stats) 