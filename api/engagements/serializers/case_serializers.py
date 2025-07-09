from rest_framework import serializers
from engagements.models import Case
from engagements.serializers.work_item_serializers import WorkItemSerializer

class CaseSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Case
        fields = WorkItemSerializer.Meta.fields + ['case_reference', 'legal_area', 'court_date'] 