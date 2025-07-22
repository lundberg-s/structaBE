from rest_framework import serializers
from engagements.models import Ticket
from engagements.serializers.work_item_serializers import WorkItemSerializer, WorkItemWritableSerializer


class TicketListSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'status', 'category', 'priority',
            'deadline', 'tenant', 'created_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_at'] 
class TicketSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Ticket
        fields = WorkItemSerializer.Meta.fields + ['ticket_number', 'reported_by', 'urgency']

class TicketWritableSerializer(WorkItemWritableSerializer):
    class Meta(WorkItemWritableSerializer.Meta):
        model = Ticket
        fields = WorkItemWritableSerializer.Meta.fields + ['ticket_number', 'reported_by', 'urgency']

class TicketCreateSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket creation - no related data loading"""
    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'status', 'category', 'priority',
            'deadline', 'ticket_number', 'reported_by', 'urgency',
            'created_at', 'updated_at', 'tenant'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'tenant'] 