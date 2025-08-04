from django.contrib import admin
from core.models import AuditLog
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'entity_type', 'entity_name', 'activity_type', 
        'created_by_username', 'risk_level_badge', 'compliance_category', 'created_at'
    )
    list_filter = (
        'activity_type', 'entity_type', 'risk_level', 'compliance_category', 
        'created_at', 'tenant', 'created_by'
    )
    search_fields = (
        'entity_name', 'description', 'business_process', 'transaction_id',
        'session_id'
    )
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'created_by', 'updated_by',
        'tenant', 'entity_type', 'entity_id', 'entity_name', 'activity_type',
        'description', 'change_summary_display', 'old_values_display', 'new_values_display',
        'session_id', 'ip_address', 'user_agent', 'business_process',
        'transaction_id', 'compliance_category', 'risk_level', 'is_immutable'
    )
    ordering = ('-created_at',)
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Audit Information', {
            'fields': (
                'id', 'activity_type', 'description', 'entity_type', 
                'entity_id', 'entity_name', 'tenant'
            ),
            'description': 'Core audit trail information'
        }),
        ('Change Tracking', {
            'fields': ('change_summary', 'old_values', 'new_values'),
            'classes': ('collapse',),
            'description': 'Detailed change tracking data'
        }),
        ('Forensic Data', {
            'fields': (
                'session_id', 'ip_address', 'user_agent', 'business_process',
                'transaction_id'
            ),
            'classes': ('collapse',),
            'description': 'Forensic and technical tracking information'
        }),
        ('Compliance & Risk', {
            'fields': ('compliance_category', 'risk_level'),
            'description': 'Compliance and risk assessment data'
        }),
        ('User & Metadata', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at', 'is_immutable'),
            'classes': ('collapse',),
            'description': 'User attribution and metadata'
        }),
    )
    
    def created_by_username(self, obj):
        """Display username with link to user admin."""
        if obj.created_by:
            try:
                from users.models import User
                user = User.objects.get(id=obj.created_by)
                url = reverse('admin:users_user_change', args=[user.id])
                return format_html('<a href="{}">{}</a>', url, user.username)
            except User.DoesNotExist:
                return f'User {obj.created_by} (not found)'
        return '-'
    created_by_username.short_description = 'Created By'
    created_by_username.admin_order_field = 'created_by'
    
    def risk_level_badge(self, obj):
        """Display risk level as a colored badge."""
        risk_colors = {
            'low': 'green',
            'medium': 'orange', 
            'high': 'red',
            'critical': 'darkred'
        }
        color = risk_colors.get(obj.risk_level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.risk_level.upper()
        )
    risk_level_badge.short_description = 'Risk Level'
    risk_level_badge.admin_order_field = 'risk_level'
    
    def entity_link(self, obj):
        """Create a link to the entity if possible."""
        if obj.entity_type and obj.entity_id:
            # This would need to be customized based on your URL structure
            return format_html(
                '<a href="#" onclick="alert(\'Entity: {} - {}\')">{}</a>',
                obj.entity_type, obj.entity_id, obj.entity_name
            )
        return obj.entity_name
    entity_link.short_description = 'Entity'
    entity_link.admin_order_field = 'entity_name'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for better performance."""
        return super().get_queryset(request).select_related(
            'updated_by', 'tenant'
        )
    
    def has_add_permission(self, request):
        """Audit logs should not be manually created."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Audit logs are immutable and cannot be changed."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Audit logs should not be deleted for compliance reasons."""
        return False
    
    def change_summary_display(self, obj):
        """Display change summary in a readable format."""
        if obj.change_summary:
            return format_html(
                '<pre style="max-height: 200px; overflow-y: auto;">{}</pre>',
                json.dumps(obj.change_summary, indent=2)
            )
        return '-'
    change_summary_display.short_description = 'Change Summary'
    
    def old_values_display(self, obj):
        """Display old values in a readable format."""
        if obj.old_values:
            return format_html(
                '<pre style="max-height: 200px; overflow-y: auto;">{}</pre>',
                json.dumps(obj.old_values, indent=2)
            )
        return '-'
    old_values_display.short_description = 'Old Values'
    
    def new_values_display(self, obj):
        """Display new values in a readable format."""
        if obj.new_values:
            return format_html(
                '<pre style="max-height: 200px; overflow-y: auto;">{}</pre>',
                json.dumps(obj.new_values, indent=2)
            )
        return '-'
    new_values_display.short_description = 'New Values'
    
    # Override the readonly fields to use custom display methods
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'created_by', 'updated_by',
        'tenant', 'entity_type', 'entity_id', 'entity_name', 'activity_type',
        'description', 'change_summary_display', 'old_values_display', 'new_values_display',
        'session_id', 'ip_address', 'user_agent', 'business_process',
        'transaction_id', 'compliance_category', 'risk_level', 'is_immutable'
    )
    
    actions = ['export_audit_logs', 'mark_high_risk_reviewed']
    
    def export_audit_logs(self, request, queryset):
        """Export selected audit logs to CSV."""
        import csv
        from django.http import HttpResponse
        from django.utils import timezone
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="audit_logs_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Entity Type', 'Entity Name', 'Activity Type', 'Description',
            'Created By', 'Created At', 'Risk Level', 'Compliance Category',
            'IP Address', 'Session ID', 'Transaction ID'
        ])
        
        for log in queryset:
            # Handle created_by as UUID
            created_by_username = ''
            if log.created_by:
                try:
                    from users.models import User
                    user = User.objects.get(id=log.created_by)
                    created_by_username = user.username
                except User.DoesNotExist:
                    created_by_username = f'User {log.created_by} (not found)'
            
            writer.writerow([
                log.id, log.entity_type, log.entity_name, log.activity_type,
                log.description, created_by_username,
                log.created_at, log.risk_level, log.compliance_category,
                log.ip_address, log.session_id, log.transaction_id
            ])
        
        return response
    export_audit_logs.short_description = "Export selected audit logs to CSV"
    
    def mark_high_risk_reviewed(self, request, queryset):
        """Mark high-risk audit logs as reviewed (for compliance purposes)."""
        high_risk_logs = queryset.filter(risk_level__in=['high', 'critical'])
        count = high_risk_logs.count()
        
        # Note: Since audit logs are immutable, we can't actually modify them
        # This action serves as a compliance workflow marker
        self.message_user(
            request, 
            f"Marked {count} high-risk audit logs for compliance review. "
            "Note: Audit logs are immutable and cannot be modified."
        )
    mark_high_risk_reviewed.short_description = "Mark high-risk logs for compliance review"
    
    def get_actions(self, request):
        """Customize available actions based on user permissions."""
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            # Remove sensitive actions for non-superusers
            if 'mark_high_risk_reviewed' in actions:
                del actions['mark_high_risk_reviewed']
        return actions 