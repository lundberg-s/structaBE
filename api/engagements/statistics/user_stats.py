from django.db.models import Count

def get_avg_per_user(qs):
    assigned_counts = (
        qs.values('assigned_user__username')
        .annotate(count=Count('id'))
        .exclude(assigned_user__isnull=True)
    )
    if assigned_counts:
        return sum([item['count'] for item in assigned_counts]) / max(len(assigned_counts), 1)
    return 0

def get_by_assigned_user(qs):
    assigned = (
        qs.values('assigned_user__username')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    return {item['assigned_user__username'] or 'Unassigned': item['count'] for item in assigned}

def get_by_created_user(qs):
    created = (
        qs.values('created_by__username')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    return {item['created_by__username']: item['count'] for item in created} 