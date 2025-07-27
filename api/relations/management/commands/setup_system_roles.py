from django.core.management.base import BaseCommand
from relations.models import Role


class Command(BaseCommand):
    help = 'Create standard system roles'

    def handle(self, *args, **options):
        system_roles = [
            "Super User",
            "Admin", 
            "User",
            "Read Only",
            "Tenant",
            "Tenant Owner",
            "Tenant Employee",
            "Tenant Admin"
        ]
        
        created_count = 0
        for role_label in system_roles:
            role, created = Role.objects.get_or_create(
                label=role_label,
                is_system=True,
                defaults={'tenant': None}
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created system role: {role_label}")
            else:
                self.stdout.write(f"System role already exists: {role_label}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} system roles')
        ) 