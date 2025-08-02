from django.contrib import admin
from core.models import Tenant
from core.mixins import AdminAuditMixin


@admin.register(Tenant)
class TenantAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ('id', 'subscription_plan', 'subscription_status', 'billing_email', 'created_at', 'updated_at')
    list_filter = ('subscription_plan', 'subscription_status', 'created_at')
    search_fields = ('billing_email',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def get_entity_type(self, obj):
        """Override to map Tenant model to 'tenant' entity type."""
        return 'tenant'
    
    def get_compliance_category(self, obj, activity_type):
        """Override to mark tenant operations as security-related."""
        return 'security'
    
    def get_business_process(self, obj):
        """Override to map tenant operations to Access Management."""
        return 'Access Management' 