from django.core.management.base import BaseCommand
from core.models import Tenant
from engagements.models import WorkItemStatus


class Command(BaseCommand):
    help = 'Seed default work item statuses for all tenants'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        
        if not tenants.exists():
            self.stdout.write(
                self.style.WARNING('No tenants found. Please create tenants first.')
            )
            return
        
        # Default statuses to seed
        default_statuses = [
            {
                'label': 'Open',
                'translated_label': '',
                'use_translation': False,
                'color': '#10B981',
                'sort_order': 1
            },
            {
                'label': 'In Progress',
                'translated_label': '',
                'use_translation': False,
                'color': '#3B82F6',
                'sort_order': 2
            },
            {
                'label': 'On Hold',
                'translated_label': '',
                'use_translation': False,
                'color': '#F59E0B',
                'sort_order': 3
            },
            {
                'label': 'Resolved',
                'translated_label': '',
                'use_translation': False,
                'color': '#8B5CF6',
                'sort_order': 4
            },
            {
                'label': 'Closed',
                'translated_label': '',
                'use_translation': False,
                'color': '#6B7280',
                'sort_order': 5
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for tenant in tenants:
            for status_data in default_statuses:
                status, created = WorkItemStatus.objects.get_or_create(
                    tenant=tenant,
                    label=status_data['label'],
                    defaults={
                        'translated_label': status_data['translated_label'],
                        'use_translation': status_data['use_translation'],
                        'color': status_data['color'],
                        'sort_order': status_data['sort_order'],
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    # Update existing status if needed
                    updated = False
                    for field, value in status_data.items():
                        if getattr(status, field) != value:
                            setattr(status, field, value)
                            updated = True
                    
                    if updated:
                        status.save()
                        updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded work item statuses: '
                f'{created_count} created, {updated_count} updated'
            )
        ) 