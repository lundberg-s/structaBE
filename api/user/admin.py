from django.contrib import admin
from .models import User, Tenant, Party, Person, Organization, Role
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('id', 'party_type', 'party_name', 'party_details', 'tenant_access', 'roles_count', 'user_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('id', 'person__first_name', 'person__last_name', 'person__email', 'organization__name', 'organization__organization_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def tenant_access(self, obj):
        """Show tenant access - either through organization ownership or user account"""
        if hasattr(obj, 'organization') and obj.organization and hasattr(obj.organization, 'tenant_obj') and obj.organization.tenant_obj:
            return f"{obj.organization.tenant_obj}"
        elif hasattr(obj, 'person') and obj.person and hasattr(obj.person, 'user') and obj.person.user and obj.person.user.tenant:
            return f" {obj.person.user.tenant}"
        return 'No tenant access'
    tenant_access.short_description = 'Tenant'
    
    def party_type(self, obj):
        """Show whether this is a Person or Organization"""
        if hasattr(obj, 'person'):
            return 'Person'
        elif hasattr(obj, 'organization'):
            return 'Organization'
        return 'Unknown'
    party_type.short_description = 'Type'
    party_type.admin_order_field = 'person__first_name'  # For sorting
    
    def party_name(self, obj):
        """Show the name of the Person or Organization"""
        if hasattr(obj, 'person') and obj.person:
            return f"{obj.person.first_name} {obj.person.last_name}"
        elif hasattr(obj, 'organization') and obj.organization:
            return obj.organization.name
        return 'N/A'
    party_name.short_description = 'Name'
    party_name.admin_order_field = 'person__first_name'
    
    def party_details(self, obj):
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
    party_details.short_description = 'Details'
    
    def roles_count(self, obj):
        """Show how many roles this party has"""
        count = obj.roles.count()
        return count if count > 0 else '-'
    roles_count.short_description = 'Roles'
    roles_count.admin_order_field = 'roles__count'
    
    def user_count(self, obj):
        """Show if this party has a user account"""
        if hasattr(obj, 'user'):
            return 'Yes' if obj.user else 'No'
        return 'N/A'
    user_count.short_description = 'Has User'

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'has_user', 'user_tenant', 'roles_count', 'created_at')
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
        """Show the tenant through the user account"""
        if hasattr(obj, 'user') and obj.user and obj.user.tenant:
            return obj.user.tenant
        return 'No tenant access'
    user_tenant.short_description = 'Tenant'
    
    def roles_count(self, obj):
        count = obj.roles.count()
        return count if count > 0 else '-'
    roles_count.short_description = 'Roles'

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization_number', 'has_tenant', 'tenant_obj', 'roles_count', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant_obj')
    search_fields = ('name', 'organization_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)
    
    def get_queryset(self, request):
        """Optimize queryset to reduce database queries"""
        return super().get_queryset(request).select_related('tenant_obj')
    
    def has_tenant(self, obj):
        return 'Yes' if hasattr(obj, 'tenant_obj') and obj.tenant_obj else 'No'
    has_tenant.short_description = 'Has Tenant'
    
    def roles_count(self, obj):
        count = obj.roles.count()
        return count if count > 0 else '-'
    roles_count.short_description = 'Roles'

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'party_name', 'party_type', 'role_type', 'party_tenant_access', 'created_at')
    list_filter = ('role_type', 'created_at', 'updated_at')
    search_fields = ('party__person__first_name', 'party__person__last_name', 'party__organization__name', 'role_type')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def party_tenant_access(self, obj):
        """Show tenant access for the party"""
        party = obj.party
        if hasattr(party, 'organization') and party.organization and hasattr(party.organization, 'tenant_obj') and party.organization.tenant_obj:
            return f"{party.organization.tenant_obj}"
        elif hasattr(party, 'person') and party.person and hasattr(party.person, 'user') and party.person.user and party.person.user.tenant:
            return f"{party.person.user.tenant}"
        return 'No tenant access'
    party_tenant_access.short_description = 'Tenant'
    
    def party_name(self, obj):
        if hasattr(obj.party, 'person') and obj.party.person:
            return f"{obj.party.person.first_name} {obj.party.person.last_name}"
        elif hasattr(obj.party, 'organization') and obj.party.organization:
            return obj.party.organization.name
        return str(obj.party)
    party_name.short_description = 'Party Name'
    party_name.admin_order_field = 'party__person__first_name'
    
    def party_type(self, obj):
        if hasattr(obj.party, 'person'):
            return 'Person'
        elif hasattr(obj.party, 'organization'):
            return 'Organization'
        return 'Unknown'
    party_type.short_description = 'Party Type'
    
    def party_tenant(self, obj):
        """Show the tenant associated with this party"""
        if hasattr(obj.party, 'tenant_obj') and obj.party.tenant_obj:
            return obj.party.tenant_obj
        return 'No tenant'
    party_tenant.short_description = 'Tenant'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    def tenant(self, obj):
        return obj.party.tenant_obj if obj.party and hasattr(obj.party, 'tenant_obj') else None
    tenant.admin_order_field = 'party__tenant_obj'
    tenant.short_description = 'Tenant'

    list_display = ('email', 'username', 'tenant', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'tenant')
    search_fields = ('email', 'username')
    ordering = ('email',)
    base_fieldsets = BaseUserAdmin.fieldsets if BaseUserAdmin.fieldsets is not None else tuple()
    fieldsets = base_fieldsets + (
        (None, {'fields': ('party', 'tenant', 'footer_text', 'external_id')}),
    )

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'subscription_plan', 'subscription_status', 'created_at', 'updated_at')
    list_filter = ('subscription_plan', 'subscription_status', 'created_at')
    search_fields = ('party__name', 'billing_email')
    readonly_fields = ('id', 'created_at', 'updated_at')

    def company_name(self, obj):
        party = obj.party
        if isinstance(party, Organization):
            return party.name
        elif isinstance(party, Person):
            return f"{party.first_name} {party.last_name}"
        return str(party)
    company_name.admin_order_field = 'party__name'
    company_name.short_description = 'Company Name'
