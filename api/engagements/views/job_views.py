from engagements.views.work_item_views import BaseWorkItemListView, BaseWorkItemDetailView

from engagements.serializers.job_serializers import JobSerializer

from engagements.models import Job

from core.choices import WorkItemType


class JobListView(BaseWorkItemListView):
    model = Job
    serializer_class = JobSerializer
    allowed_type = WorkItemType.JOB
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']

class JobDetailView(BaseWorkItemDetailView):
    model = Job
    serializer_class = JobSerializer
    allowed_type = WorkItemType.JOB