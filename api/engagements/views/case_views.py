from engagements.serializers.case_serializers import CaseSerializer
from engagements.views.work_item_views import BaseWorkItemListView, BaseWorkItemDetailView

from engagements.models import Case

from core.models import WorkItemType


class CaseListView(BaseWorkItemListView):
    model = Case
    serializer_class = CaseSerializer
    allowed_type = WorkItemType.CASE
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']

class CaseDetailView(BaseWorkItemDetailView):
    model = Case
    serializer_class = CaseSerializer
    allowed_type = WorkItemType.CASE