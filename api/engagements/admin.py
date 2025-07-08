from django.contrib import admin
from engagements.models import WorkItem, Ticket, Case, Job, Attachment, Comment, ActivityLog, WorkItemPartnerRole, Assignment

@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'category', 'created_by', 'tenant', 'created_at']
    list_filter = ['status', 'priority', 'category', 'tenant', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    readonly_fields = ['assigned_by', 'assigned_at']

class WorkItemPartnerRoleInline(admin.TabularInline):
    model = WorkItemPartnerRole
    extra = 0

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'ticket_number', 'urgency', 'reported_by', 'status', 'tenant', 'created_at']
    list_filter = ['urgency', 'status', 'tenant', 'created_at']
    search_fields = ['title', 'ticket_number', 'reported_by']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [WorkItemPartnerRoleInline, AssignmentInline]

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'case_reference', 'legal_area', 'status', 'priority', 'category', 'created_by', 'tenant', 'created_at']
    list_filter = ['status', 'priority', 'category', 'legal_area', 'tenant', 'created_at']
    search_fields = ['title', 'case_reference', 'legal_area', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [AssignmentInline]

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'job_code', 'assigned_team', 'estimated_hours', 'status', 'tenant', 'created_at']
    list_filter = ['assigned_team', 'status', 'tenant', 'created_at']
    search_fields = ['title', 'job_code', 'assigned_team']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['work_item', 'user', 'assigned_by', 'assigned_at']
    list_filter = ['assigned_by', 'assigned_at']
    search_fields = ['work_item__title', 'user__email', 'assigned_by__email']
    readonly_fields = ['assigned_at']

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'work_item', 'uploaded_by', 'file_size', 'tenant', 'created_at']
    list_filter = ['created_at', 'tenant']
    search_fields = ['filename', 'work_item__title']
    readonly_fields = ['id', 'created_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'work_item', 'tenant', 'created_at']
    list_filter = ['created_at', 'tenant']
    search_fields = ['content', 'work_item__title', 'author__username']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'user', 'work_item', 'tenant', 'created_at']
    list_filter = ['activity_type', 'created_at', 'tenant']
    search_fields = ['description', 'work_item__title', 'user__username']
    readonly_fields = ['id', 'created_at']

@admin.register(WorkItemPartnerRole)
class WorkItemPartnerRoleAdmin(admin.ModelAdmin):
    list_display = ['work_item', 'partner', 'role', 'tenant']
    list_filter = ['role', 'tenant']
    search_fields = ['work_item__title', 'role']
    readonly_fields = ['id']
