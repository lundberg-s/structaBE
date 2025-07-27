from enum import Enum

class SystemRole(Enum):
    SUPER_USER = "super_user"
    ADMIN = "admin"
    USER = "user"
    READ_ONLY = "readonly"
    TENANT = "tenant"
    TENANT_OWNER = "tenant_owner"
    TENANT_EMPLOYEE = "tenant_employee"
    TENANT_ADMIN = "tenant_admin"

    @classmethod
    def choices(cls):
        return [(role.value, role.name.replace('_', ' ').title()) for role in cls]

    @classmethod
    def labels(cls):
        return {role.value: role.name.replace('_', ' ').title() for role in cls}
