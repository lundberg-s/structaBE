from django.db import models

class RelationObjectType(models.TextChoices):
    PERSON = 'person', 'Person'
    ORGANIZATION = 'organization', 'Organization'
    WORKITEM = 'workitem', 'WorkItem'


class SystemRole(models.TextChoices):
    SUPER_USER = 'super_user', 'Super User'
    ADMIN = 'admin', 'Admin'
    USER = 'user', 'User'
    READ_ONLY = 'readonly', 'Read Only'
    TENANT_OWNER = 'tenant_owner', 'Tenant Owner'
    TENANT_EMPLOYEE = 'tenant_employee', 'Tenant Employee'
    TENANT_ADMIN = 'tenant_admin', 'Tenant Admin'
    CONTACT_INFO = 'contact_info', 'Contact Info'
    CUSTOMER = 'customer', 'Customer'
    VENDOR = 'vendor', 'Vendor'


class RelationType(models.TextChoices):
    # Partner to Partner relationships
    CUSTOMER = 'customer', 'Customer'
    VENDOR = 'vendor', 'Vendor'
    SUPPLIER = 'supplier', 'Supplier'
    PARTNER = 'partner', 'Partner'
    COMPETITOR = 'competitor', 'Competitor'
    MEMBER_OF = 'member_of', 'Member Of'
    EMPLOYEE_OF = 'employee_of', 'Employee Of'
    OWNER_OF = 'owner_of', 'Owner Of'
    
    # Partner to WorkItem relationships
    ASSIGNED_TO = 'assigned_to', 'Assigned To'
    REPORTED_BY = 'reported_by', 'Reported By'
    APPROVED_BY = 'approved_by', 'Approved By'
    REVIEWED_BY = 'reviewed_by', 'Reviewed By'
    CONTACT_FOR = 'contact_for', 'Contact For'
    CLIENT_FOR = 'client_for', 'Client For'
    
    # WorkItem to WorkItem relationships
    BLOCKS = 'blocks', 'Blocks'
    DEPENDS_ON = 'depends_on', 'Depends On'
    RELATED_TO = 'related_to', 'Related To'
    DUPLICATE_OF = 'duplicate_of', 'Duplicate Of'
    PARENT_OF = 'parent_of', 'Parent Of'
    CHILD_OF = 'child_of', 'Child Of'
    
    # Generic relationships
    CONTACTS = 'contacts', 'Contacts'
    WORKS_WITH = 'works_with', 'Works With'
    REPORTS_TO = 'reports_to', 'Reports To'
    MANAGES = 'manages', 'Manages'
    COLLABORATES_WITH = 'collaborates_with', 'Collaborates With'