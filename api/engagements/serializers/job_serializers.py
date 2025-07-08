from rest_framework import serializers
from engagements.models import Job
from engagements.serializers.work_item_serializers import WorkItemSerializer

class JobSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Job
        fields = WorkItemSerializer.Meta.fields + ['job_code', 'assigned_team', 'estimated_hours'] 