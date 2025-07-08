from django.contrib import admin
from relations.models import Partner, Person, Organization, Role

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'partner_type', 'partner_name', 'partner_details', 'tenant_access', 'roles_count', 'user_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('id', 'person__first_name', 'person__last_name', 'person__email', 'organization__name', 'organization__organization_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def tenant_access(self, obj):
        """Show tenant access - partner now has direct tenant relationship"""
        if hasattr(obj, 'tenant') and obj.tenant:
            return f"{obj.tenant}"
        return 'No tenant access'
    tenant_access.short_description = 'Tenant'
    
    def partner_type(self, obj):
        """Show whether this is a Person or Organization"""
        if hasattr(obj, 'person'):
            return 'Person'
        elif hasattr(obj, 'organization'):
            return 'Organization'
        return 'Unknown'
    partner_type.short_description = 'Type'
    partner_type.admin_order_field = 'person__first_name'  # For sorting
    
    def partner_name(self, obj):
        """Show the name of the Person or Organization"""
        if hasattr(obj, 'person') and obj.person:
            return f"{obj.person.first_name} {obj.person.last_name}"
        elif hasattr(obj, 'organization') and obj.organization:
            return obj.organization.name
        return 'N/A'
    partner_name.short_description = 'Name'
    partner_name.admin_order_field = 'person__first_name'
    
    def partner_details(self, obj):
        """Show additional details like email for Person or org number for Organization"""
        if hasattr(obj, 'person') and obj.person:
            details = []
            if obj.person.email:
                details.append(f"Email: {obj.person.email}")
            if obj.person.phone:
                details.append(f"Phone: {obj.person.phone}")
            return " | ".join(details) if details else "No contact info"
        elif hasattr(obj, 'organization') and obj.organization:
            if obj.organization.organization_number:
                return f"Org #: {obj.organization.organization_number}"
            return "No org number"
        return 'N/A'
    partner_details.short_description = 'Details'
    
    def roles_count(self, obj):
        """Show how many roles this partner has"""
        count = obj.roles.count()
        return count if count > 0 else '-'
    roles_count.short_description = 'Roles'
    roles_count.admin_order_field = 'roles__count'
    
    def user_count(self, obj):
        """Show if this partner has a user account"""
        if hasattr(obj, 'user'):
            return 'Yes' if obj.user else 'No'
        return 'N/A'
    user_count.short_description = 'Has User'

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'has_user', 'user_tenant', 'role', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('first_name', 'last_name')
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'
    
    def has_user(self, obj):
        return 'Yes' if hasattr(obj, 'user') and obj.user else 'No'
    has_user.short_description = 'Has User Account'
    
    def user_tenant(self, obj):
        """Show the tenant - person now has direct tenant relationship"""
        if hasattr(obj, 'tenant') and obj.tenant:
            return obj.tenant
        return 'No tenant access'
    user_tenant.short_description = 'Tenant'
    
    def role(self, obj):
        role = obj.roles.first()
        return role.get_role_type_display() if role else "-"
    role.short_description = 'Role'

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization_number', 'has_tenant', 'tenant', 'role', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant')
    search_fields = ('name', 'organization_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)
    
    def get_queryset(self, request):
        """Optimize queryset to reduce database queries"""
        return super().get_queryset(request).select_related('tenant')
    
    def has_tenant(self, obj):
        return 'Yes' if hasattr(obj, 'tenant') and obj.tenant else 'No'
    has_tenant.short_description = 'Has Tenant'
    
    def role(self, obj):
        role = obj.roles.first()
        return role.get_role_type_display() if role else "-"
    role.short_description = 'Role'

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'partner_name', 'partner_type', 'role_type', 'partner_tenant_access', 'created_at')
    list_filter = ('role_type', 'created_at', 'updated_at')
    search_fields = ('partner__person__first_name', 'partner__person__last_name', 'partner__organization__name', 'role_type')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def partner_tenant_access(self, obj):
        """Show tenant access for the partner"""
        partner = obj.partner
        if hasattr(partner, 'tenant') and partner.tenant:
            return f"{partner.tenant}"
        return 'No tenant access'
    partner_tenant_access.short_description = 'Tenant'
    
    def partner_name(self, obj):
        if hasattr(obj.partner, 'person') and obj.partner.person:
            return f"{obj.partner.person.first_name} {obj.partner.person.last_name}"
        elif hasattr(obj.partner, 'organization') and obj.partner.organization:
            return obj.partner.organization.name
        return str(obj.partner)
    partner_name.short_description = 'Partner Name'
    partner_name.admin_order_field = 'partner__person__first_name'
    
    def partner_type(self, obj):
        if hasattr(obj.partner, 'person'):
            return 'Person'
        elif hasattr(obj.partner, 'organization'):
            return 'Organization'
        return 'Unknown'
    partner_type.short_description = 'Partner Type'
    
    def partner_tenant(self, obj):
        """Show the tenant associated with this partner"""
        if hasattr(obj.partner, 'tenant') and obj.partner.tenant:
            return obj.partner.tenant
        return 'No tenant'
    partner_tenant.short_description = 'Tenant'


# Register your models here.
