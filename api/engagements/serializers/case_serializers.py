from rest_framework import serializers
from engagements.models import Case
from engagements.serializers.work_item_serializers import WorkItemSerializer, WorkItemListSerializer, WorkItemCreateSerializer, WorkItemUpdateSerializer

class CaseListSerializer(WorkItemListSerializer):
    class Meta(WorkItemListSerializer.Meta):
        model = Case
        fields = WorkItemListSerializer.Meta.fields + ['case_reference', 'legal_area', 'court_date']
        read_only_fields = WorkItemListSerializer.Meta.read_only_fields + ['case_reference', 'legal_area', 'court_date']

class CaseSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Case
        fields = WorkItemSerializer.Meta.fields + ['case_reference', 'legal_area', 'court_date'] 

class CaseCreateSerializer(WorkItemCreateSerializer):
    class Meta(WorkItemCreateSerializer.Meta):
        model = Case
        fields = WorkItemCreateSerializer.Meta.fields + ['case_reference', 'legal_area', 'court_date']
        read_only_fields = WorkItemCreateSerializer.Meta.read_only_fields + ['case_reference', 'legal_area', 'court_date']

class CaseUpdateSerializer(WorkItemUpdateSerializer):
    class Meta(WorkItemUpdateSerializer.Meta):
        model = Case
        fields = WorkItemUpdateSerializer.Meta.fields + ['case_reference', 'legal_area', 'court_date']
        read_only_fields = WorkItemUpdateSerializer.Meta.read_only_fields + ['case_reference', 'legal_area', 'court_date']  