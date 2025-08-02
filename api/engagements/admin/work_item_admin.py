from django.contrib import admin
from engagements.models import WorkItem
from core.mixins.admin_mixins import AdminAuditMixin


@admin.register(WorkItem)
class WorkItemAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'category', 'tenant', 'created_at']
    list_filter = ['status', 'priority', 'category', 'tenant', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at'] 