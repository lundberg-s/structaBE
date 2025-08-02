from engagements.models import Ticket
from engagements.serializers.work_item_serializers import (
    WorkItemSerializer,
    WorkItemListSerializer,
    WorkItemCreateSerializer,
    WorkItemUpdateSerializer,
)


class TicketListSerializer(WorkItemListSerializer):
    class Meta(WorkItemListSerializer.Meta):
        model = Ticket
        fields = WorkItemListSerializer.Meta.fields + [
            "ticket_number",
        ]
        read_only_fields = WorkItemListSerializer.Meta.read_only_fields + [
            "ticket_number",
        ]


class TicketSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Ticket
        fields = WorkItemSerializer.Meta.fields + [
            "ticket_number",
        ]
        read_only_fields = WorkItemSerializer.Meta.read_only_fields + [
            "ticket_number",
        ]
    

class TicketCreateSerializer(WorkItemCreateSerializer):
    """Lightweight serializer for ticket creation - no related data loading"""

    class Meta(WorkItemCreateSerializer.Meta):
        model = Ticket
        fields = WorkItemCreateSerializer.Meta.fields + [
            "ticket_number",
        ]
        read_only_fields = WorkItemCreateSerializer.Meta.read_only_fields + [
            "ticket_number",
        ]


class TicketUpdateSerializer(WorkItemUpdateSerializer):
    class Meta(WorkItemUpdateSerializer.Meta):
        model = Ticket
        fields = WorkItemUpdateSerializer.Meta.fields + [
            "ticket_number",
        ]
        read_only_fields = WorkItemUpdateSerializer.Meta.read_only_fields + [
            "ticket_number",
        ]
