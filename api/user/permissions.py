from rest_framework.permissions import BasePermission
from user.models import PartyRoleTypes

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
    allowed_roles = [PartyRoleTypes.TENANT_OWNER, PartyRoleTypes.TENANT_ADMIN]

class CanManageUsersAndRoles(HasAnyRole):
    allowed_roles = [PartyRoleTypes.TENANT_OWNER, PartyRoleTypes.TENANT_ADMIN, PartyRoleTypes.MANAGER]

class CanViewBillingInfo(HasAnyRole):
    allowed_roles = [PartyRoleTypes.TENANT_OWNER, PartyRoleTypes.TENANT_ADMIN, PartyRoleTypes.BILLING]

class CanModifyBillingInfo(HasAnyRole):
    allowed_roles = [PartyRoleTypes.TENANT_OWNER, PartyRoleTypes.TENANT_ADMIN, PartyRoleTypes.BILLING]

class CanCreateEditDeleteContent(HasAnyRole):
    allowed_roles = [PartyRoleTypes.TENANT_OWNER, PartyRoleTypes.TENANT_ADMIN, PartyRoleTypes.MANAGER, PartyRoleTypes.MEMBER, PartyRoleTypes.EMPLOYEE]

class CanViewContentOnly(HasAnyRole):
    allowed_roles = [PartyRoleTypes.TENANT_OWNER, PartyRoleTypes.TENANT_ADMIN, PartyRoleTypes.MANAGER, PartyRoleTypes.MEMBER, PartyRoleTypes.BILLING, PartyRoleTypes.READ_ONLY, PartyRoleTypes.CUSTOMER, PartyRoleTypes.VENDOR, PartyRoleTypes.EMPLOYEE]

class CanAccessCustomerData(HasAnyRole):
    allowed_roles = [PartyRoleTypes.TENANT_OWNER, PartyRoleTypes.TENANT_ADMIN, PartyRoleTypes.MANAGER, PartyRoleTypes.MEMBER, PartyRoleTypes.BILLING, PartyRoleTypes.CUSTOMER, PartyRoleTypes.EMPLOYEE]

class CanManageVendors(HasAnyRole):
    allowed_roles = [PartyRoleTypes.TENANT_OWNER, PartyRoleTypes.TENANT_ADMIN, PartyRoleTypes.MANAGER, PartyRoleTypes.VENDOR]

class CanPerformAudits(HasAnyRole):
    allowed_roles = [PartyRoleTypes.TENANT_OWNER, PartyRoleTypes.TENANT_ADMIN, PartyRoleTypes.MANAGER]