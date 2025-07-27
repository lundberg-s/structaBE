from django.contrib import admin
from relations.models import Partner, Person, Organization, Relation, Assignment
from core.admin_mixins import AdminAuditMixin


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
class PersonAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'role', 'tenant', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('first_name', 'last_name')
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'


@admin.register(Organization)
class OrganizationAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'organization_number', 'role', 'tenant', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant')
    search_fields = ('name', 'organization_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)


@admin.register(Relation)
class RelationAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ('id', 'relationship_description', 'tenant', 'created_at')
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
    readonly_fields = ('id', 'created_at', 'updated_at', 'relationship_description')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Relationship Information', {
            'fields': ('relationship_description', 'source_partner', 'source_workitem', 'source_type', 'target_partner', 'target_workitem', 'target_type', 'role', 'tenant'),
            'description': 'Source → Role → Target: The role reflects the SOURCE\'s perspective. Source is the entity that "owns" the relationship, Target is who the relationship is "to".'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def relationship_description(self, obj):
        """Show the relationship in Source → Role → Target format"""
        return obj.get_relationship_description()
    relationship_description.short_description = 'Relationship'
    
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


@admin.register(Assignment)
class AssignmentAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ('id', 'relation', 'tenant', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant')
    search_fields = ('relation__source_partner__person__first_name', 'relation__source_partner__person__last_name', 'relation__source_workitem__title', 'relation__target_partner__person__first_name', 'relation__target_partner__person__last_name', 'relation__target_workitem__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)