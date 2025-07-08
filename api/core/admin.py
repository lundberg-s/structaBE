from django.contrib import admin
from core.models import Tenant
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscription_plan', 'subscription_status', 'billing_email', 'created_at', 'updated_at')
    list_filter = ('subscription_plan', 'subscription_status', 'created_at')
    search_fields = ('billing_email',)
    readonly_fields = ('id', 'created_at', 'updated_at')
