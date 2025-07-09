from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import datetime, timedelta

def get_total(qs):
    return qs.count()

def get_by_field(qs, field):
    return dict(qs.values_list(field).annotate(count=Count('id')))

def get_created_per_period(qs, period='month'):
    if period == 'month':
        trunc = TruncMonth('created_at')
        key = 'month'
    else:
        trunc = TruncWeek('created_at')
        key = 'week'
    per_period = (
        qs.annotate(period=trunc)
          .values('period')
          .annotate(count=Count('id'))
          .order_by('period')
    )
    return {str(item['period']): item['count'] for item in per_period}

def get_open_at_month_end(qs, months):
    open_cases_month = {}
    for month in months:
        year, m = map(int, month.split('-'))
        last_day = datetime(year, m, 28) + timedelta(days=4)
        last_day = last_day - timedelta(days=last_day.day)
        count = qs.filter(created_at__lte=last_day, status__in=['open', 'in-progress']).count()
        open_cases_month[month] = count
    return open_cases_month

def get_unassigned(qs):
    return qs.filter(assigned_user__isnull=True).count()

def get_longest_open(qs):
    open_items = qs.filter(status__in=['open', 'in-progress']).order_by('created_at')[:10]
    return [
        {
            'id': str(item.id),
            'title': item.title,
            'created_at': item.created_at,
            'status': item.status,
            'assigned_user': item.assigned_user.username if hasattr(item, 'assigned_user') and item.assigned_user else None
        }
        for item in open_items
    ]

def get_overdue(qs, now):
    return qs.filter(deadline__lt=now, status__in=['open', 'in-progress']).count() 