from django.contrib import admin
from relations.models import Organization
from core.mixins import AdminAuditMixin


@admin.register(Organization)
class OrganizationAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'organization_number', 'role', 'tenant', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant')
    search_fields = ('name', 'organization_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',) 