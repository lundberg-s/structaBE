from django.contrib import admin
from engagements.models import Case
from core.mixins.admin_mixins import AdminAuditMixin


@admin.register(Case)
class CaseAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['title', 'case_reference', 'legal_area', 'status', 'tenant', 'created_at']
    list_filter = ['legal_area', 'status', 'tenant', 'created_at']
    search_fields = ['title', 'case_reference', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at'] 