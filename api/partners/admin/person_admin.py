from django.contrib import admin
from partners.models import Person
from core.mixins import AdminAuditMixin


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