from django.contrib import admin
from engagements.models import WorkItemCategory
from core.mixins import AdminAuditMixin


@admin.register(WorkItemCategory)
class WorkItemCategoryAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['label', 'translated_label', 'use_translation', 'color', 'sort_order', 'tenant', 'is_active']
    list_filter = ['is_active', 'use_translation', 'tenant', 'created_at']
    search_fields = ['label', 'translated_label']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['sort_order', 'label']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'label', 'translated_label', 'use_translation')
        }),
        ('Appearance', {
            'fields': ('color', 'sort_order')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Audit Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant') 