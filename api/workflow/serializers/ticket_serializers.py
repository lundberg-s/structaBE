from rest_framework import serializers
from workflow.models import Ticket
from workflow.serializers.work_item_serializers import WorkItemSerializer, WorkItemWritableSerializer

class TicketSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Ticket
        fields = WorkItemSerializer.Meta.fields + ['ticket_number', 'reported_by', 'urgency']

class TicketWritableSerializer(WorkItemWritableSerializer):
    class Meta(WorkItemWritableSerializer.Meta):
        model = Ticket
        fields = WorkItemWritableSerializer.Meta.fields + ['ticket_number', 'reported_by', 'urgency'] 