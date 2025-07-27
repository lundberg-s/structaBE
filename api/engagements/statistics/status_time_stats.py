from django.utils import timezone
from core.models import AuditLog

def get_avg_time_in_status(qs, AuditLog, now):
    """Calculate average time items spend in each status."""
    total_time = 0
    count = 0
    
    for item in qs:
        logs = list(AuditLog.objects.filter(
            content_type__model='workitem',
            object_id=item.id, 
            activity_type='status_changed'
        ).order_by('created_at'))
        
        if len(logs) >= 2:
            for i in range(len(logs) - 1):
                time_diff = logs[i + 1].created_at - logs[i].created_at
                total_time += time_diff.total_seconds() / 3600  # Convert to hours
                count += 1
    
    return total_time / count if count > 0 else 0

def get_reopened_count(qs, AuditLog):
    """Count how many times items were reopened (status changed back to open)."""
    reopened_count = 0
    
    for item in qs:
        logs = AuditLog.objects.filter(
            content_type__model='workitem',
            object_id=item.id, 
            activity_type='status_changed'
        ).order_by('created_at')
        
        # Count transitions back to 'open' status
        for log in logs:
            if 'open' in log.description.lower():
                reopened_count += 1
    
    return reopened_count 