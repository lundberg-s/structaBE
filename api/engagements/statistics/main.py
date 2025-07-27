from django.utils import timezone
from engagements.models import WorkItem, Ticket, Case, Job
from core.models import AuditLog
from django.db import models

def get_work_item_statistics(model, tenant, Comment, AuditLog):
    """Get statistics for a specific work item type."""
    now = timezone.now()
    qs = model.objects.filter(tenant=tenant, is_deleted=False)
    
    stats = {
        'total': qs.count(),
        'open': qs.filter(status='open').count(),
        'in_progress': qs.filter(status='in_progress').count(),
        'on_hold': qs.filter(status='on_hold').count(),
        'resolved': qs.filter(status='resolved').count(),
        'closed': qs.filter(status='closed').count(),
        'high_priority': qs.filter(priority='high').count(),
        'urgent_priority': qs.filter(priority='urgent').count(),
        'avg_time_in_status_hours': get_avg_time_in_status(qs, AuditLog, now),
        'reopened': get_reopened_count(qs, AuditLog),
    }
    
    # Add model-specific stats
    if model == Ticket:
        stats['avg_resolution_time_hours'] = get_avg_resolution_time(qs, now)
        stats['tickets_by_urgency'] = {
            'low': qs.filter(urgency='low').count(),
            'medium': qs.filter(urgency='medium').count(),
            'high': qs.filter(urgency='high').count(),
        }
    elif model == Case:
        stats['cases_by_legal_area'] = {}
        for case in qs.values('legal_area').distinct():
            area = case['legal_area']
            stats['cases_by_legal_area'][area] = qs.filter(legal_area=area).count()
    elif model == Job:
        stats['total_estimated_hours'] = sum(qs.values_list('estimated_hours', flat=True))
        stats['avg_estimated_hours'] = qs.aggregate(avg=models.Avg('estimated_hours'))['avg'] or 0
    
    return stats

def get_avg_resolution_time(qs, now):
    """Calculate average resolution time for resolved items."""
    resolved_items = qs.filter(status__in=['resolved', 'closed'])
    if not resolved_items.exists():
        return 0
    
    total_time = 0
    count = 0
    
    for item in resolved_items:
        # Find the first status change to 'resolved' or 'closed'
        resolution_log = AuditLog.objects.filter(
            content_type__model='workitem',
            object_id=item.id,
            activity_type='status_changed',
            description__icontains='resolved'
        ).first()
        
        if resolution_log:
            time_diff = resolution_log.created_at - item.created_at
            total_time += time_diff.total_seconds() / 3600  # Convert to hours
            count += 1
    
    return total_time / count if count > 0 else 0

def get_all_work_item_statistics(tenant, Comment, AuditLog, WorkItem):
    """Get statistics for all work item types."""
    stats = {}
    
    for subclass in [Ticket, Case, Job]:
        stats[subclass.__name__.lower()] = get_work_item_statistics(subclass, tenant, Comment, AuditLog)
    
    return stats 