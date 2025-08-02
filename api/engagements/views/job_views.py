from engagements.views.work_item_views import (
    BaseWorkItemListView,
    BaseWorkItemDetailView,
)

from engagements.serializers.job_serializers import (
    JobSerializer,
    JobListSerializer,
    JobCreateSerializer,
    JobUpdateSerializer,
)

from engagements.models import Job
from core.choices import WorkItemType


class JobListView(BaseWorkItemListView):
    model = Job
    allowed_type = WorkItemType.JOB
    filterset_fields = ["status__label", "priority__label", "category__label"]
    search_fields = ["title", "description"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return JobListSerializer
        elif self.request.method == "POST":
            return JobCreateSerializer
        return JobSerializer


class JobDetailView(BaseWorkItemDetailView):
    model = Job
    allowed_type = WorkItemType.JOB

    def get_serializer_class(self):
        if self.request.method == "GET":
            return JobSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return JobUpdateSerializer
        return JobSerializer