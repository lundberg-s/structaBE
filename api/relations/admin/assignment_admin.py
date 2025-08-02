from django.contrib import admin
from relations.models import Assignment
from core.admin_mixins import AdminAuditMixin


@admin.register(Assignment)
class AssignmentAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ('id', 'relation', 'tenant', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant')
    search_fields = ('relation__source_partner__person__first_name', 'relation__source_partner__person__last_name', 'relation__source_workitem__title', 'relation__target_partner__person__first_name', 'relation__target_partner__person__last_name', 'relation__target_workitem__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',) 