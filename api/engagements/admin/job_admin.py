from django.contrib import admin
from engagements.models import Job
from core.mixins.admin_mixins import AdminAuditMixin


@admin.register(Job)
class JobAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['title', 'job_code', 'estimated_hours', 'status', 'tenant', 'created_at']
    list_filter = ['status', 'tenant', 'created_at']
    search_fields = ['title', 'job_code', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at'] 