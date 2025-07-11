# Tenant Roles Permission Matrix

| Permission/Action              | tenant_owner | tenant_admin | tenant_manager | tenant_billing | tenant_employee | tenant_readonly |
|--------------------------------|--------------|--------------|---------------|----------------|----------------|-----------------|
| **Manage tenant settings**     | ✅           | ✅           | ❌            | ❌             | ❌             | ❌              |
| **Transfer/delete tenant**     | ✅           | ❌           | ❌            | ❌             | ❌             | ❌              |
| **Manage users & roles**       | ✅           | ✅           | ✅            | ❌             | ❌             | ❌              |
| **Deactivate/remove users**    | ✅           | ✅           | ✅            | ❌             | ❌             | ❌              |
| **View billing info**          | ✅           | ✅           | ❌            | ✅             | ❌             | ❌              |
| **Modify billing info**        | ✅           | ✅           | ❌            | ✅             | ❌             | ❌              |
| **Create/edit/delete content** | ✅           | ✅           | ✅            | ❌             | ✅             | ❌              |
| **View content only**          | ✅           | ✅           | ✅            | ✅             | ✅             | ✅              |
| **Export data/reports**        | ✅           | ✅           | ✅            | ✅             | ❌             | ❌              |
| **Access customer data**       | ✅           | ✅           | ✅            | ✅             | ✅             | ❌              |
| **Manage vendors**             | ✅           | ✅           | ✅            | ❌             | ❌             | ❌              |
| **Perform audits/log access**  | ✅           | ✅           | ✅            | ❌             | ❌             | ❌              |

---

## Role Descriptions

- **tenant_owner:** Full control, including transfer/delete tenant. (e.g., Company CEO)
- **tenant_admin:** Almost full control, cannot transfer/delete tenant. (e.g., IT Admin)
- **tenant_manager:** Manages users, content, vendors, audits. (e.g., Department Manager)
- **tenant_billing:** Manages billing only. (e.g., Finance Staff)
- **tenant_employee:** Can create/edit content, no user/billing management. (e.g., Regular Staff)
- **tenant_readonly:** View-only access to all tenant data. (e.g., Auditor, External Reviewer)

---

## Usage Notes

- Users can have multiple roles.
- Enforce permissions in your application logic based on these roles.
- Consider implementing helper functions or decorators to simplify permission checks.
