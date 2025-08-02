from django.contrib import admin
from core.models import Role
from core.mixins import AdminAuditMixin


@admin.register(Role)
class RoleAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ('id', 'key', 'label', 'is_system', 'tenant', 'created_at')
    list_filter = ('is_system', 'created_at', 'updated_at', 'tenant')
    search_fields = ('key', 'label')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Role Information', {
            'fields': ('key', 'label', 'is_system', 'tenant'),
            'description': 'Create roles for the system. System roles are available to all tenants.'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 