from django.db.models import F, ExpressionWrapper, DurationField, Avg
from datetime import timedelta

def get_sla_compliance(qs):
    sla_days = 3
    resolved = qs.filter(status='resolved', updated_at__isnull=False)
    if resolved.exists():
        within_sla = resolved.filter(updated_at__lte=F('created_at') + timedelta(days=sla_days)).count()
        return round(100 * within_sla / resolved.count(), 2)
    return None

def get_avg_resolution_time(qs):
    resolved = qs.filter(status='resolved', updated_at__isnull=False)
    if resolved.exists():
        avg_resolution = resolved.annotate(
            resolution_time=ExpressionWrapper(F('updated_at') - F('created_at'), output_field=DurationField())
        ).aggregate(avg=Avg('resolution_time'))
        return round(avg_resolution['avg'].total_seconds() / 86400, 2) if avg_resolution['avg'] else None
    return None 