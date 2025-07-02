from django.contrib import admin
from .models import User, Tenant
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'tenant', 'is_staff', 'is_active')
    list_filter = ('tenant', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)
    base_fieldsets = BaseUserAdmin.fieldsets if BaseUserAdmin.fieldsets is not None else tuple()
    fieldsets = base_fieldsets + (
        (None, {'fields': ('tenant', 'footer_text', 'external_id')}),
    )

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'subscription_plan', 'subscription_status', 'workitem_type', 'created_at', 'updated_at')
    list_filter = ('subscription_plan', 'subscription_status', 'workitem_type', 'created_at')
    search_fields = ('name', 'billing_email', 'payment_customer_id')
    readonly_fields = ('id', 'created_at', 'updated_at')