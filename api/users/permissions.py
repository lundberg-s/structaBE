from rest_framework.permissions import BasePermission
from relations.models import PartnerRoleTypes

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

# --- Tenant Role Permission Classes (Matrix-aligned) ---

class CanManageTenantSettings(HasAnyRole):
    """Manage tenant settings (owner, admin)"""
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN]

class CanTransferOrDeleteTenant(HasAnyRole):
    """Transfer or delete tenant (owner only)"""
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER]

class CanManageUsersAndRoles(HasAnyRole):
    """Manage users & roles (owner, admin, manager)"""
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER]

class CanDeactivateRemoveUsers(HasAnyRole):
    """Deactivate/remove users (owner, admin, manager)"""
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER]

class CanViewBillingInfo(HasAnyRole):
    """View billing info (owner, admin, billing)"""
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_BILLING]

class CanModifyBillingInfo(HasAnyRole):
    """Modify billing info (owner, admin, billing)"""
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_BILLING]

class CanCreateEditDeleteContent(HasAnyRole):
    """Create/edit/delete content (owner, admin, manager, employee)"""
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER, PartnerRoleTypes.TENANT_EMPLOYEE]

class CanViewContentOnly(HasAnyRole):
    """View content only (all tenant roles)"""
    allowed_roles = [
        PartnerRoleTypes.TENANT_OWNER,
        PartnerRoleTypes.TENANT_ADMIN,
        PartnerRoleTypes.TENANT_MANAGER,
        PartnerRoleTypes.TENANT_BILLING,
        PartnerRoleTypes.TENANT_EMPLOYEE,
        PartnerRoleTypes.TENANT_READ_ONLY,
    ]

class CanExportDataOrReports(HasAnyRole):
    """Export data/reports (owner, admin, manager, billing)"""
    allowed_roles = [
        PartnerRoleTypes.TENANT_OWNER,
        PartnerRoleTypes.TENANT_ADMIN,
        PartnerRoleTypes.TENANT_MANAGER,
        PartnerRoleTypes.TENANT_BILLING,
    ]

class CanAccessCustomerData(HasAnyRole):
    """Access customer data (owner, admin, manager, billing, employee)"""
    allowed_roles = [
        PartnerRoleTypes.TENANT_OWNER,
        PartnerRoleTypes.TENANT_ADMIN,
        PartnerRoleTypes.TENANT_MANAGER,
        PartnerRoleTypes.TENANT_BILLING,
        PartnerRoleTypes.TENANT_EMPLOYEE,
    ]

class CanManageVendors(HasAnyRole):
    """Manage vendors (owner, admin, manager)"""
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER]

class CanPerformAudits(HasAnyRole):
    """Perform audits/log access (owner, admin, manager)"""
    allowed_roles = [PartnerRoleTypes.TENANT_OWNER, PartnerRoleTypes.TENANT_ADMIN, PartnerRoleTypes.TENANT_MANAGER]