from django.contrib import admin
from engagements.models import Comment
from core.mixins.admin_mixins import AdminAuditMixin


@admin.register(Comment)
class CommentAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['work_item', 'created_by', 'tenant', 'created_at']
    list_filter = ['tenant', 'created_at']
    search_fields = ['content', 'work_item__title']
    readonly_fields = ['id', 'created_at'] 