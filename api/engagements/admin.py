from django.contrib import admin
from engagements.models import WorkItem, Ticket, Case, Job, Attachment, Comment, Assignment
from core.admin_mixins import AdminAuditMixin


@admin.register(WorkItem)
class WorkItemAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'category', 'tenant', 'created_at']
    list_filter = ['status', 'priority', 'category', 'tenant', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Ticket)
class TicketAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['title', 'ticket_number', 'urgency', 'status', 'tenant', 'created_at']
    list_filter = ['urgency', 'status', 'tenant', 'created_at']
    search_fields = ['title', 'ticket_number', 'description']
    readonly_fields = ['id', 'ticket_number', 'created_at', 'updated_at']


@admin.register(Case)
class CaseAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['title', 'case_reference', 'legal_area', 'status', 'tenant', 'created_at']
    list_filter = ['legal_area', 'status', 'tenant', 'created_at']
    search_fields = ['title', 'case_reference', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Job)
class JobAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['title', 'job_code', 'estimated_hours', 'status', 'tenant', 'created_at']
    list_filter = ['status', 'tenant', 'created_at']
    search_fields = ['title', 'job_code', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Attachment)
class AttachmentAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['filename', 'work_item', 'file_size', 'mime_type', 'tenant', 'created_at']
    list_filter = ['mime_type', 'tenant', 'created_at']
    search_fields = ['filename', 'work_item__title']
    readonly_fields = ['id', 'file_size', 'created_at']


@admin.register(Comment)
class CommentAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['work_item', 'created_by', 'tenant', 'created_at']
    list_filter = ['tenant', 'created_at']
    search_fields = ['content', 'work_item__title']
    readonly_fields = ['id', 'created_at']


@admin.register(Assignment)
class AssignmentAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['work_item', 'user', 'tenant', 'created_at']
    list_filter = ['tenant', 'created_at']
    search_fields = ['work_item__title', 'user__username']
    readonly_fields = ['id', 'created_at']
