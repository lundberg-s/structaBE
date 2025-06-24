from django.contrib import admin
from diarium.models import Case, Attachment, Comment, ActivityLog

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'category', 'created_by', 'assigned_user', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'case', 'uploaded_by', 'file_size', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['filename', 'case__title']
    readonly_fields = ['id', 'uploaded_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'case', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'case__title', 'author__username']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'user', 'case', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['description', 'case__title', 'user__username']
    readonly_fields = ['id', 'created_at']
