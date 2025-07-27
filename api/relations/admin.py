from django.contrib import admin
from relations.models import Partner, Person, Organization, Role, Relation


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


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'role', 'tenant', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('first_name', 'last_name')
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization_number', 'role', 'tenant', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant')
    search_fields = ('name', 'organization_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'is_system', 'tenant', 'created_at')
    list_filter = ('is_system', 'created_at', 'updated_at', 'tenant')
    search_fields = ('label',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Role Information', {
            'fields': ('label', 'is_system', 'tenant'),
            'description': 'Create roles for the system. System roles are available to all tenants.'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_display', 'role', 'target_display', 'tenant', 'created_at')
    list_filter = ('role', 'created_at', 'updated_at', 'tenant')
    search_fields = (
        'source_partner__person__first_name', 
        'source_partner__person__last_name', 
        'source_partner__organization__name',
        'target_partner__person__first_name', 
        'target_partner__person__last_name', 
        'target_partner__organization__name',
        'source_workitem__title',
        'target_workitem__title',
        'role__label'
    )
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Relation Information', {
            'fields': ('source_partner', 'source_workitem', 'source_type', 'target_partner', 'target_workitem', 'target_type', 'role', 'tenant'),
            'description': 'Create relationships between partners and work items using direct FKs.'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def source_display(self, obj):
        """Show the source in a readable format"""
        if obj.source_partner:
            if hasattr(obj.source_partner, 'person'):
                return f"👤 {obj.source_partner.person.first_name} {obj.source_partner.person.last_name}"
            elif hasattr(obj.source_partner, 'organization'):
                return f"🏢 {obj.source_partner.organization.name}"
        elif obj.source_workitem:
            return f"📋 {obj.source_workitem.title}"
        return 'Unknown'
    source_display.short_description = 'Source'
    
    def target_display(self, obj):
        """Show the target in a readable format"""
        if obj.target_partner:
            if hasattr(obj.target_partner, 'person'):
                return f"👤 {obj.target_partner.person.first_name} {obj.target_partner.person.last_name}"
            elif hasattr(obj.target_partner, 'organization'):
                return f"🏢 {obj.target_partner.organization.name}"
        elif obj.target_workitem:
            return f"📋 {obj.target_workitem.title}"
        return 'Unknown'
    target_display.short_description = 'Target'
