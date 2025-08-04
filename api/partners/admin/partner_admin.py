from django.contrib import admin
from partners.models import Partner


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'partner_type', 'partner_name', 'role', 'tenant', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant')
    search_fields = ('id', 'person__first_name', 'person__last_name', 'person__email', 'organization__name', 'organization__organization_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def partner_type(self, obj):
        """Show whether this is a Person or Organization"""
        if hasattr(obj, 'person'):
            return 'Person'
        elif hasattr(obj, 'organization'):
            return 'Organization'
        return 'Unknown'
    partner_type.short_description = 'Type'
    
    def partner_name(self, obj):
        """Show the name of the partner"""
        if hasattr(obj, 'person'):
            return f"{obj.person.first_name} {obj.person.last_name}"
        elif hasattr(obj, 'organization'):
            return obj.organization.name
        return 'Unknown'
    partner_name.short_description = 'Name' 