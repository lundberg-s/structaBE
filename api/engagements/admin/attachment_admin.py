from django.contrib import admin
from engagements.models import Attachment
from core.mixins.admin_mixins import AdminAuditMixin


@admin.register(Attachment)
class AttachmentAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ['filename', 'work_item', 'file_size', 'mime_type', 'tenant', 'created_at']
    list_filter = ['mime_type', 'tenant', 'created_at']
    search_fields = ['filename', 'work_item__title']
    readonly_fields = ['id', 'file_size', 'created_at'] 