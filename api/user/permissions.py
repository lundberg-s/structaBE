from rest_framework.permissions import BasePermission
from user.models import PartnerRoleTypes

# Helper function to check if a user has any of the allowed roles

def user_has_role(user, roles):
    partner = getattr(user, 'partner', None)
    if not partner:
        return False
    return partner.roles.filter(role_type__in=roles).exists()

# Generic base permission class
class HasAnyRole(BasePermission):
    allowed_roles = []
    def has_permission(self, request, view):
        partner = getattr(request.user, 'partner', None)
        if not partner:
            return False
        return partner.roles.filter(role_type__in=self.allowed_roles).exists()

# Specific permission classes for each action in the matrix
class CanManageTenantSettings(HasAnyRole):
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN]

class CanManageUsersAndRoles(HasAnyRole):
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER]

class CanViewBillingInfo(HasAnyRole):
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_BILLING]

class CanModifyBillingInfo(HasAnyRole):
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_BILLING]

class CanCreateEditDeleteContent(HasAnyRole):
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER, PartnerRoleTypes.TENANT_EMPLOYEE]

class CanViewContentOnly(HasAnyRole):
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER, PartnerRoleTypes.TENANT_EMPLOYEE, PartnerRoleTypes.TENANT_READ_ONLY]

class CanAccessCustomerData(HasAnyRole):
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER, PartnerRoleTypes.TENANT_EMPLOYEE]

class CanManageVendors(HasAnyRole):
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER]

class CanPerformAudits(HasAnyRole):
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER]