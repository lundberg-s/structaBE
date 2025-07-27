from django.contrib import admin
from core.models import Tenant
from core.models import Role
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscription_plan', 'subscription_status', 'billing_email', 'created_at', 'updated_at')
    list_filter = ('subscription_plan', 'subscription_status', 'created_at')
    search_fields = ('billing_email',)
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
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
