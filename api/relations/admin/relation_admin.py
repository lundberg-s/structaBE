from django.contrib import admin
from relations.models import Relation
from core.mixins.admin_mixins import AdminAuditMixin


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