from django.contrib import admin
from users.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.admin_mixins import AdminAuditMixin


@admin.register(User)
class UserAdmin(AdminAuditMixin, BaseUserAdmin):
    def tenant(self, obj):
        return obj.tenant if obj.tenant else None
    tenant.admin_order_field = 'tenant'
    tenant.short_description = 'Tenant'

    def related_partner_object(self, obj):
        return obj.partner.person if obj.partner and obj.partner.person else None
    related_partner_object.admin_order_field = 'partner__person'
    related_partner_object.short_description = 'Related Partner Object'

    list_display = ('email', 'username', 'tenant', 'related_partner_object', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'tenant')
    search_fields = ('email', 'username')
    ordering = ('email',)
    base_fieldsets = BaseUserAdmin.fieldsets if BaseUserAdmin.fieldsets is not None else tuple()
    fieldsets = base_fieldsets + (
        (None, {'fields': ('partner', 'tenant')}),
    )
    
    def get_entity_type(self, obj):
        """Override to map User model to 'user' entity type."""
        return 'user'
    
    def get_compliance_category(self, obj, activity_type):
        """Override to mark user operations as security-related."""
        return 'security'
    
    def get_business_process(self, obj):
        """Override to map user operations to Access Management."""
        return 'Access Management'
