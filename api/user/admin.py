from django.contrib import admin
from .models import User, Tenant
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    def tenant(self, obj):
        return obj.party.tenant if obj.party and obj.party.tenant else None
    tenant.admin_order_field = 'party__tenant'
    tenant.short_description = 'Tenant'

    list_display = ('email', 'username', 'tenant', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)
    base_fieldsets = BaseUserAdmin.fieldsets if BaseUserAdmin.fieldsets is not None else tuple()
    fieldsets = base_fieldsets + (
        (None, {'fields': ('party', 'footer_text', 'external_id')}),
    )

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'subscription_plan', 'subscription_status', 'created_at', 'updated_at')
    list_filter = ('subscription_plan', 'subscription_status', 'created_at')
    search_fields = ('party__name', 'billing_email')
    readonly_fields = ('id', 'created_at', 'updated_at')

    def company_name(self, obj):
        return obj.party.name if obj.party else ""
    company_name.admin_order_field = 'party__name'
    company_name.short_description = 'Company Name'