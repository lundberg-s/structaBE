from django.contrib import admin
from engagements.models import Ticket
from core.mixins import AdminAuditMixin


@admin.register(Ticket)
class TicketAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['title', 'ticket_number', 'urgency', 'status', 'tenant', 'created_at']
    list_filter = ['urgency', 'status', 'tenant', 'created_at']
    search_fields = ['title', 'ticket_number', 'description']
    readonly_fields = ['id', 'ticket_number', 'created_at', 'updated_at'] 