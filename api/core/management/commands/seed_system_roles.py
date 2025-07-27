from django.core.management.base import BaseCommand
from core.models import Role
from core.enums.system_role_enums import SystemRole

class Command(BaseCommand):
    help = "Seed system roles into the database"

    def handle(self, *args, **kwargs):
        for role in SystemRole:
            obj, created = Role.objects.get_or_create(
                key=role.value,
                defaults={
                    "label": role.name.replace('_', ' ').title(),
                    "is_system": True,
                    "tenant": None,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created system role: {obj.key}"))
            else:
                self.stdout.write(f"System role {obj.key} already exists")
