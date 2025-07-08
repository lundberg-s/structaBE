from rest_framework import serializers
from workflow.models import Job
from workflow.serializers.work_item_serializers import WorkItemSerializer

class JobSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Job
        fields = WorkItemSerializer.Meta.fields + ['job_code', 'assigned_team', 'estimated_hours'] 