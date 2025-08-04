from django.core.management.base import BaseCommand
from core.models import Tenant
from engagements.models import WorkItemStatus, WorkItemPriority, WorkItemCategory


class Command(BaseCommand):
    help = 'Seed all default work item options (statuses, priorities, categories) for all tenants'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        
        if not tenants.exists():
            self.stdout.write(
                self.style.WARNING('No tenants found. Please create tenants first.')
            )
            return
        
        # Default statuses
        default_statuses = [
            {'label': 'Open', 'color': '#10B981', 'sort_order': 1},
            {'label': 'In Progress', 'color': '#3B82F6', 'sort_order': 2},
            {'label': 'On Hold', 'color': '#F59E0B', 'sort_order': 3},
            {'label': 'Resolved', 'color': '#8B5CF6', 'sort_order': 4},
            {'label': 'Closed', 'color': '#6B7280', 'sort_order': 5},
        ]
        
        # Default priorities
        default_priorities = [
            {'label': 'Low', 'color': '#10B981', 'sort_order': 1},
            {'label': 'Medium', 'color': '#F59E0B', 'sort_order': 2},
            {'label': 'High', 'color': '#EF4444', 'sort_order': 3},
            {'label': 'Urgent', 'color': '#DC2626', 'sort_order': 4},
        ]
        
        # Default categories
        default_categories = [
            {'label': 'Bug', 'color': '#EF4444', 'sort_order': 1},
            {'label': 'Feature', 'color': '#10B981', 'sort_order': 2},
            {'label': 'Task', 'color': '#3B82F6', 'sort_order': 3},
            {'label': 'Improvement', 'color': '#8B5CF6', 'sort_order': 4},
            {'label': 'Support', 'color': '#F59E0B', 'sort_order': 5},
        ]
        
        total_created = 0
        total_updated = 0
        
        for tenant in tenants:
            self.stdout.write(f'Processing tenant: {tenant.id}')
            
            # Seed statuses
            for status_data in default_statuses:
                status, created = WorkItemStatus.objects.get_or_create(
                    tenant=tenant,
                    label=status_data['label'],
                    defaults={
                        'translated_label': '',
                        'use_translation': False,
                        'color': status_data['color'],
                        'sort_order': status_data['sort_order'],
                        'is_active': True
                    }
                )
                if created:
                    total_created += 1
                else:
                    total_updated += 1
            
            # Seed priorities
            for priority_data in default_priorities:
                priority, created = WorkItemPriority.objects.get_or_create(
                    tenant=tenant,
                    label=priority_data['label'],
                    defaults={
                        'translated_label': '',
                        'use_translation': False,
                        'color': priority_data['color'],
                        'sort_order': priority_data['sort_order'],
                        'is_active': True
                    }
                )
                if created:
                    total_created += 1
                else:
                    total_updated += 1
            
            # Seed categories
            for category_data in default_categories:
                category, created = WorkItemCategory.objects.get_or_create(
                    tenant=tenant,
                    label=category_data['label'],
                    defaults={
                        'translated_label': '',
                        'use_translation': False,
                        'color': category_data['color'],
                        'sort_order': category_data['sort_order'],
                        'is_active': True
                    }
                )
                if created:
                    total_created += 1
                else:
                    total_updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded all work item options: '
                f'{total_created} created, {total_updated} updated'
            )
        ) 