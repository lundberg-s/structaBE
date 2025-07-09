# Tenant Roles Permission Matrix

| Permission/Action              | tenant_owner | tenant_admin | manager | member | billing | readonly | customer | vendor | employee |
|--------------------------------|--------------|--------------|---------|--------|---------|----------|----------|--------|----------|
| **Manage tenant settings**     | ✅           | ✅           | ❌      | ❌     | ❌      | ❌       | ❌       | ❌     | ❌       |
| **Manage users & roles**       | ✅           | ✅           | ✅      | ❌     | ❌      | ❌       | ❌       | ❌     | ❌       |
| **View billing info**          | ✅           | ✅           | ❌      | ❌     | ✅      | ❌       | ❌       | ❌     | ❌       |
| **Modify billing info**        | ✅           | ✅           | ❌      | ❌     | ✅      | ❌       | ❌       | ❌     | ❌       |
| **Create/edit/delete content** | ✅           | ✅           | ✅      | ✅     | ❌      | ❌       | ❌       | ❌     | ✅       |
| **View content only**          | ✅           | ✅           | ✅      | ✅     | ✅      | ✅       | ✅       | ✅     | ✅       |
| **Access customer data**       | ✅           | ✅           | ✅      | ✅     | ✅      | ❌       | ✅       | ❌     | ✅       |
| **Manage vendors**             | ✅           | ✅           | ✅      | ❌     | ❌      | ❌       | ❌       | ✅     | ❌       |
| **Perform audits/log access**  | ✅           | ✅           | ✅      | ❌     | ❌      | ❌       | ❌       | ❌     | ❌       |

---

## Role Descriptions

- **tenant_owner**: Full control over tenant settings, billing, users, content, and audit logs.
- **tenant_admin**: Almost full control, excluding some owner-only features.
- **manager**: Manage users, content, vendors, and audits but no billing or tenant settings.
- **member**: Create and modify content; no user or billing management.
- **billing**: Access and modify billing information only.
- **readonly**: View-only access to all tenant data.
- **customer**: Access limited to customer-related data and features.
- **vendor**: Manage vendor-specific tasks.
- **employee**: Internal user with operational access, similar to member but possibly restricted.

---

## Usage Notes

- Users can have multiple roles.
- Enforce permissions in your application logic based on these roles.
- Consider implementing helper functions or decorators to simplify permission checks.
