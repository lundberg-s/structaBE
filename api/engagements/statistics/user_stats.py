from django.db.models import Count
from users.models import User

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
    # Get all unique created_by UUIDs
    created_by_ids = qs.values_list('created_by', flat=True).exclude(created_by__isnull=True).distinct()
    
    # Fetch all users in one query
    users = User.objects.filter(id__in=created_by_ids)
    users_dict = {user.id: user.email for user in users}
    
    # Get counts by created_by
    created = (
        qs.values('created_by')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Map UUIDs to user emails
    result = {}
    for item in created:
        user_email = users_dict.get(item['created_by'], f'User {item["created_by"]}')
        result[user_email] = item['count']
    
    return result 