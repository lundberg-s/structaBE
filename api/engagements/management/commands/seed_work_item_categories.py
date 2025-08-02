from django.core.management.base import BaseCommand
from core.models import Tenant
from engagements.models import WorkItemCategory


class Command(BaseCommand):
    help = 'Seed default work item categories for all tenants'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        
        if not tenants.exists():
            self.stdout.write(
                self.style.WARNING('No tenants found. Please create tenants first.')
            )
            return
        
        # Default categories to seed
        default_categories = [
            {
                'label': 'Bug',
                'translated_label': '',
                'use_translation': False,
                'color': '#EF4444',
                'sort_order': 1
            },
            {
                'label': 'Feature',
                'translated_label': '',
                'use_translation': False,
                'color': '#10B981',
                'sort_order': 2
            },
            {
                'label': 'Task',
                'translated_label': '',
                'use_translation': False,
                'color': '#3B82F6',
                'sort_order': 3
            },
            {
                'label': 'Improvement',
                'translated_label': '',
                'use_translation': False,
                'color': '#8B5CF6',
                'sort_order': 4
            },
            {
                'label': 'Support',
                'translated_label': '',
                'use_translation': False,
                'color': '#F59E0B',
                'sort_order': 5
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for tenant in tenants:
            for category_data in default_categories:
                category, created = WorkItemCategory.objects.get_or_create(
                    tenant=tenant,
                    label=category_data['label'],
                    defaults={
                        'translated_label': category_data['translated_label'],
                        'use_translation': category_data['use_translation'],
                        'color': category_data['color'],
                        'sort_order': category_data['sort_order'],
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    # Update existing category if needed
                    updated = False
                    for field, value in category_data.items():
                        if getattr(category, field) != value:
                            setattr(category, field, value)
                            updated = True
                    
                    if updated:
                        category.save()
                        updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded work item categories: '
                f'{created_count} created, {updated_count} updated'
            )
        ) 