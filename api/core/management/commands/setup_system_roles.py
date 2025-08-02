from django.core.management.base import BaseCommand
from core.models import Role
from core.enums import SystemRole


class Command(BaseCommand):
    help = 'Create standard system roles'

    def handle(self, *args, **options):
        system_roles = [
            (SystemRole.SUPER_USER, "Super User"),
            (SystemRole.ADMIN, "Admin"), 
            (SystemRole.USER, "User"),
            (SystemRole.READ_ONLY, "Read Only"),
            (SystemRole.TENANT, "Tenant"),
            (SystemRole.TENANT_OWNER, "Tenant Owner"),
            (SystemRole.TENANT_EMPLOYEE, "Tenant Employee"),
            (SystemRole.TENANT_ADMIN, "Tenant Admin"),
            (SystemRole.CONTACT_INFO, "Contact Info"),
            (SystemRole.CUSTOMER, "Customer"),
            (SystemRole.VENDOR, "Vendor"),
        ]
        
        created_count = 0
        for role_key, role_label in system_roles:
            role, created = Role.objects.get_or_create(
                key=role_key.value,
                is_system=True,
                defaults={
                    'label': role_label,
                    'tenant': None
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created system role: {role_label} ({role_key.value})")
            else:
                self.stdout.write(f"System role already exists: {role_label} ({role_key.value})")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} system roles')
        ) 