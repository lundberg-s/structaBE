from django.utils import timezone
from .work_item_stats import *
from .user_stats import *
from .comment_stats import *
from .status_time_stats import *
from .sla_stats import *

def get_work_item_statistics(model, tenant, Comment, ActivityLog):
    stats = {}
    now = timezone.now()
    qs = model.objects.filter(tenant=tenant)

    stats['total'] = get_total(qs)
    for field in ['status', 'priority', 'category']:
        if hasattr(model, field):
            stats[f'by_{field}'] = get_by_field(qs, field)

    if hasattr(model, 'created_at'):
        stats['created_per_month'] = get_created_per_period(qs, 'month')
        stats['created_per_week'] = get_created_per_period(qs, 'week')

    if hasattr(model, 'status') and hasattr(model, 'updated_at'):
        resolved_qs = qs.filter(status='resolved')
        stats['resolved_per_month'] = get_created_per_period(resolved_qs, 'month')
        stats['resolved_per_week'] = get_created_per_period(resolved_qs, 'week')

    if hasattr(model, 'created_at') and hasattr(model, 'status'):
        months = list(stats.get('created_per_month', {}).keys())[-12:]
        stats['open_at_month_end'] = get_open_at_month_end(qs, months)

    if hasattr(model, 'assigned_user'):
        stats['avg_per_user'] = get_avg_per_user(qs)
        stats['by_assigned_user'] = get_by_assigned_user(qs)
        stats['unassigned'] = get_unassigned(qs)

    if hasattr(model, 'created_by'):
        stats['by_created_user'] = get_by_created_user(qs)

    if hasattr(model, 'comments'):
        stats['avg_time_to_first_response_hours'] = get_avg_time_to_first_response(qs, Comment)

    if hasattr(model, 'activity_log'):
        stats['avg_time_in_status_hours'] = get_avg_time_in_status(qs, ActivityLog, now)
        stats['reopened'] = get_reopened_count(qs, ActivityLog)

    if hasattr(model, 'deadline') and hasattr(model, 'status'):
        stats['overdue'] = get_overdue(qs, now)

    if hasattr(model, 'status') and hasattr(model, 'created_at'):
        stats['longest_open'] = get_longest_open(qs)

    if hasattr(model, 'status') and hasattr(model, 'created_at') and hasattr(model, 'updated_at'):
        stats['sla_compliance_percent'] = get_sla_compliance(qs)
        stats['average_resolution_time_days'] = get_avg_resolution_time(qs)

    return stats

def get_all_work_item_statistics(tenant, Comment, ActivityLog, WorkItem):
    subclasses = WorkItem.__subclasses__()
    stats = {}
    for subclass in subclasses:
        stats[subclass.__name__.lower()] = get_work_item_statistics(subclass, tenant, Comment, ActivityLog)
    return stats 