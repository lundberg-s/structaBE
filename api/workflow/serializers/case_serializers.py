from rest_framework import serializers
from workflow.models import Case
from workflow.serializers.work_item_serializers import WorkItemSerializer

class CaseSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Case
        fields = WorkItemSerializer.Meta.fields + ['case_reference', 'legal_area', 'court_date'] 