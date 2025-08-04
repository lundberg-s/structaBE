from core.models import Tenant, Role, AuditLog


class TenantFactory:
    @classmethod
    def create(cls, work_item_type='ticket', **kwargs):
        return Tenant.objects.create(
            work_item_type=work_item_type,
            **kwargs
        )


class RoleFactory:
    @classmethod
    def get_or_create(cls, created_by=None, **kwargs):
        role, created = Role.objects.get_or_create(
            key=kwargs.get("key", "test_role"),
            label=kwargs.get("label", "Test Role"),
            is_system=kwargs.get("is_system", False),
        )
        if created:
            role.created_by = created_by.id if created_by else None
            role.save()
        return role

    @classmethod
    def create(cls, tenant=None, created_by=None, **kwargs):
        return Role.objects.create(
            tenant=tenant,
            key=kwargs.get("key", "test_role"),
            label=kwargs.get("label", "Test Role"),
            is_system=kwargs.get("is_system", False),
            created_by=created_by.id if created_by else None,
        )


class AuditLogFactory:
    @classmethod
    def create(cls, tenant=None, created_by=None, **kwargs):
        return AuditLog.objects.create(
            tenant=tenant,
            entity_type=kwargs.get("entity_type", "ticket"),
            entity_id=kwargs.get("entity_id", "12345678-1234-1234-1234-123456789012"),
            entity_name=kwargs.get("entity_name", "Test Entity"),
            activity_type=kwargs.get("activity_type", "created"),
            description=kwargs.get("description", "Test audit log entry"),
            change_summary=kwargs.get("change_summary", {}),
            old_values=kwargs.get("old_values", None),
            new_values=kwargs.get("new_values", None),
            session_id=kwargs.get("session_id", "test-session-123"),
            ip_address=kwargs.get("ip_address", "127.0.0.1"),
            user_agent=kwargs.get("user_agent", "Test User Agent"),
            business_process=kwargs.get("business_process", "test_process"),
            transaction_id=kwargs.get("transaction_id", "test-transaction-123"),
            compliance_category=kwargs.get("compliance_category", "operational"),
            risk_level=kwargs.get("risk_level", "low"),
            created_by=created_by.id,
        )


# Legacy function for backward compatibility
def create_tenant(work_item_type='ticket'):
    return TenantFactory.create(work_item_type=work_item_type)