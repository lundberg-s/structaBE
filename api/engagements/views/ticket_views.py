from engagements.serializers.ticket_serializers import (
    TicketSerializer,
    TicketListSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
)
from engagements.views.work_item_views import (
    BaseWorkItemListView,
    BaseWorkItemDetailView,
)

from engagements.models import Ticket
from core.choices import WorkItemType


class TicketListView(BaseWorkItemListView):
    model = Ticket
    allowed_type = WorkItemType.TICKET
    filterset_fields = ["status", "priority"]
    search_fields = ["title", "description"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TicketListSerializer
        elif self.request.method == "POST":
            return TicketCreateSerializer
        return TicketSerializer


class TicketDetailView(BaseWorkItemDetailView):
    model = Ticket
    allowed_type = WorkItemType.TICKET

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TicketSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return TicketUpdateSerializer
        return TicketSerializer
