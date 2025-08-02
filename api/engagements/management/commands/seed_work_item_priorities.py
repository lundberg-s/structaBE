from django.core.management.base import BaseCommand
from core.models import Tenant
from engagements.models import WorkItemPriority


class Command(BaseCommand):
    help = 'Seed default work item priorities for all tenants'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        
        if not tenants.exists():
            self.stdout.write(
                self.style.WARNING('No tenants found. Please create tenants first.')
            )
            return
        
        # Default priorities to seed
        default_priorities = [
            {
                'label': 'Low',
                'translated_label': '',
                'use_translation': False,
                'color': '#10B981',
                'sort_order': 1
            },
            {
                'label': 'Medium',
                'translated_label': '',
                'use_translation': False,
                'color': '#F59E0B',
                'sort_order': 2
            },
            {
                'label': 'High',
                'translated_label': '',
                'use_translation': False,
                'color': '#EF4444',
                'sort_order': 3
            },
            {
                'label': 'Urgent',
                'translated_label': '',
                'use_translation': False,
                'color': '#DC2626',
                'sort_order': 4
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for tenant in tenants:
            for priority_data in default_priorities:
                priority, created = WorkItemPriority.objects.get_or_create(
                    tenant=tenant,
                    label=priority_data['label'],
                    defaults={
                        'translated_label': priority_data['translated_label'],
                        'use_translation': priority_data['use_translation'],
                        'color': priority_data['color'],
                        'sort_order': priority_data['sort_order'],
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    # Update existing priority if needed
                    updated = False
                    for field, value in priority_data.items():
                        if getattr(priority, field) != value:
                            setattr(priority, field, value)
                            updated = True
                    
                    if updated:
                        priority.save()
                        updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded work item priorities: '
                f'{created_count} created, {updated_count} updated'
            )
        ) 