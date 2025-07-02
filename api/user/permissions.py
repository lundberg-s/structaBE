from rest_framework.permissions import BasePermission

# Helper function to check if a user has any of the allowed roles

def user_has_role(user, roles):
    party = getattr(user, 'party', None)
    if not party:
        return False
    return party.roles.filter(role_type__in=roles).exists()

# Generic base permission class
class HasAnyRole(BasePermission):
    allowed_roles = []
    def has_permission(self, request, view):
        party = getattr(request.user, 'party', None)
        if not party:
            return False
        return party.roles.filter(role_type__in=self.allowed_roles).exists()

# Specific permission classes for each action in the matrix
class CanManageTenantSettings(HasAnyRole):
    allowed_roles = ['tenant_owner', 'tenant_admin']

class CanManageUsersAndRoles(HasAnyRole):
    allowed_roles = ['tenant_owner', 'tenant_admin', 'manager']

class CanViewBillingInfo(HasAnyRole):
    allowed_roles = ['tenant_owner', 'tenant_admin', 'billing']

class CanModifyBillingInfo(HasAnyRole):
    allowed_roles = ['tenant_owner', 'tenant_admin', 'billing']

class CanCreateEditDeleteContent(HasAnyRole):
    allowed_roles = ['tenant_owner', 'tenant_admin', 'manager', 'member', 'employee']

class CanViewContentOnly(HasAnyRole):
    allowed_roles = ['tenant_owner', 'tenant_admin', 'manager', 'member', 'billing', 'readonly', 'customer', 'vendor', 'employee']

class CanAccessCustomerData(HasAnyRole):
    allowed_roles = ['tenant_owner', 'tenant_admin', 'manager', 'member', 'billing', 'customer', 'employee']

class CanManageVendors(HasAnyRole):
    allowed_roles = ['tenant_owner', 'tenant_admin', 'manager', 'vendor']

class CanPerformAudits(HasAnyRole):
    allowed_roles = ['tenant_owner', 'tenant_admin', 'manager'] 