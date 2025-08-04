from engagements.views.work_item_views import (
    BaseWorkItemListView,
    BaseWorkItemDetailView,
)

from engagements.serializers.case_serializers import (
    CaseSerializer,
    CaseListSerializer,
    CaseCreateSerializer,
    CaseUpdateSerializer,
)
from engagements.models import Case

from core.choices import WorkItemType


class CaseListView(BaseWorkItemListView):
    model = Case
    allowed_type = WorkItemType.CASE
    filterset_fields = ["status__label", "priority__label", "category__label"]
    search_fields = ["title", "description"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CaseListSerializer
        elif self.request.method == "POST":
            return CaseCreateSerializer
        return CaseSerializer


class CaseDetailView(BaseWorkItemDetailView):
    model = Case
    allowed_type = WorkItemType.CASE

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CaseSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return CaseUpdateSerializer
        return CaseSerializer