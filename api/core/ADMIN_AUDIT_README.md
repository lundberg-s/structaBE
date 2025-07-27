# Admin Audit Mixin

The `AdminAuditMixin` provides automatic audit logging for Django admin interfaces. It creates professional SAP-style audit trails whenever models are created, updated, or deleted through the admin interface.

## Usage

Simply inherit from `AdminAuditMixin` in your admin classes:

```python
from django.contrib import admin
from core.admin_mixins import AdminAuditMixin
from your_app.models import YourModel

@admin.register(YourModel)
class YourModelAdmin(AdminAuditMixin, admin.ModelAdmin):
    # Your admin configuration here
    list_display = ('id', 'name', 'created_at')
    # ... other admin options
```

## Features

- **Automatic Audit Logging**: Creates audit logs for create, update, and delete operations
- **Professional SAP-style Trails**: Includes forensic data, compliance categories, and risk assessment
- **Configurable**: Override methods to customize behavior for specific models
- **Reusable**: Single mixin works for all admin interfaces

## What Gets Logged

Each audit log includes:

- **Entity Information**: Type, ID, and name of the affected record
- **Activity Details**: What action was performed (created, updated, deleted)
- **User Attribution**: Who performed the action
- **Forensic Data**: IP address, session ID, user agent, transaction ID
- **Compliance Data**: Risk level and compliance category
- **Business Context**: Business process and description

## Customization

You can override any of the mixin methods to customize behavior:

```python
class CustomModelAdmin(AdminAuditMixin, admin.ModelAdmin):
    def get_risk_level(self, obj, activity_type):
        """Custom risk assessment logic."""
        if activity_type == 'deleted' and obj.is_critical:
            return 'critical'
        return super().get_risk_level(obj, activity_type)
    
    def get_compliance_category(self, obj, activity_type):
        """Custom compliance categorization."""
        if obj.is_financial_data:
            return 'financial'
        return super().get_compliance_category(obj, activity_type)
    
    def get_business_process(self, obj):
        """Custom business process mapping."""
        return 'Custom Process'
```

## Available Override Methods

- `get_entity_type(obj)`: Map model to entity type
- `get_entity_name(obj)`: Extract human-readable name
- `get_audit_description(obj, activity_type)`: Generate description
- `get_risk_level(obj, activity_type)`: Assess risk (low/medium/high/critical)
- `get_compliance_category(obj, activity_type)`: Assign compliance category
- `get_business_process(obj)`: Map to business process

## Entity Type Mappings

The mixin automatically maps common model names to entity types:

- `person` → 'person'
- `organization` → 'organization'
- `ticket` → 'ticket'
- `case` → 'case'
- `job` → 'job'
- `role` → 'role'
- `relation` → 'relation'
- `comment` → 'comment'
- `attachment` → 'attachment'
- `assignment` → 'assignment'
- `user` → 'user'
- `tenant` → 'tenant'

## Risk Level Assessment

- **Low**: Create, update operations
- **Medium**: Export, import operations
- **High**: Delete, approve, reject operations
- **Critical**: System-critical deletions

## Compliance Categories

- **Operational**: General business operations
- **Privacy**: Personal data operations
- **Security**: Security-sensitive operations
- **Financial**: Financial data operations
- **Regulatory**: Compliance-related operations

## Business Process Mapping

- **Partner Management**: Person, Organization operations
- **Ticket Management**: Ticket operations
- **Case Management**: Case operations
- **Job Management**: Job operations
- **Relationship Management**: Relation operations
- **Communication Management**: Comment operations
- **Document Management**: Attachment operations
- **Resource Management**: Assignment operations
- **Access Management**: Role, User, Tenant operations

## Example

```python
# Before: No audit logging
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization_number')

# After: Automatic audit logging
@admin.register(Organization)
class OrganizationAdmin(AdminAuditMixin, admin.ModelAdmin):
    list_display = ('name', 'organization_number')
```

Now every create, update, or delete operation on organizations through the admin interface will automatically create a professional audit log with full forensic data and compliance information. 