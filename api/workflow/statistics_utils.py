from workflow.models import WorkItem, ActivityLog, Comment
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from collections import defaultdict
from datetime import timedelta, datetime


def get_workitem_statistics(model, tenant):
    stats = {}
    now = timezone.now()
    qs = model.objects.filter(tenant=tenant)

    # Total count
    stats['total'] = qs.count()

    # By status, priority, category (if present)
    for field in ['status', 'priority', 'category']:
        if hasattr(model, field):
            stats[f'by_{field}'] = dict(qs.values_list(field).annotate(count=Count('id')))

    # Created per month/week
    if hasattr(model, 'created_at'):
        per_month = (
            qs.annotate(month=TruncMonth('created_at'))
              .values('month')
              .annotate(count=Count('id'))
              .order_by('month')
        )
        stats['created_per_month'] = {str(item['month']): item['count'] for item in per_month}

        per_week = (
            qs.annotate(week=TruncWeek('created_at'))
              .values('week')
              .annotate(count=Count('id'))
              .order_by('week')
        )
        stats['created_per_week'] = {str(item['week']): item['count'] for item in per_week}

    # Resolved per month/week (if status field exists)
    if hasattr(model, 'status') and hasattr(model, 'updated_at'):
        resolved_qs = qs.filter(status='resolved')
        resolved_per_month = (
            resolved_qs.annotate(month=TruncMonth('updated_at'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
        )
        stats['resolved_per_month'] = {str(item['month']): item['count'] for item in resolved_per_month}

        resolved_per_week = (
            resolved_qs.annotate(week=TruncWeek('updated_at'))
                .values('week')
                .annotate(count=Count('id'))
                .order_by('week')
        )
        stats['resolved_per_week'] = {str(item['week']): item['count'] for item in resolved_per_week}

    # Open at end of each month (last 12 months)
    if hasattr(model, 'created_at') and hasattr(model, 'status'):
        open_cases_month = {}
        months = list(stats.get('created_per_month', {}).keys())[-12:]
        for month in months:
            year, m = map(int, month.split('-'))
            last_day = datetime(year, m, 28) + timedelta(days=4)
            last_day = last_day - timedelta(days=last_day.day)
            count = qs.filter(created_at__lte=last_day, status__in=['open', 'in-progress']).count()
            open_cases_month[month] = count
        stats['open_at_month_end'] = open_cases_month

    # Average number assigned per user (if assigned_user exists)
    if hasattr(model, 'assigned_user'):
        assigned_counts = (
            qs.values('assigned_user__username')
            .annotate(count=Count('id'))
            .exclude(assigned_user__isnull=True)
        )
        if assigned_counts:
            stats['avg_per_user'] = sum([item['count'] for item in assigned_counts]) / max(len(assigned_counts), 1)
        else:
            stats['avg_per_user'] = 0

        # By assigned user
        assigned = (
            qs.values('assigned_user__username')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        stats['by_assigned_user'] = {item['assigned_user__username'] or 'Unassigned': item['count'] for item in assigned}

    # By created user
    if hasattr(model, 'created_by'):
        created = (
            qs.values('created_by__username')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        stats['by_created_user'] = {item['created_by__username']: item['count'] for item in created}

    # Unassigned
    if hasattr(model, 'assigned_user'):
        stats['unassigned'] = qs.filter(assigned_user__isnull=True).count()

    # Average time to first response (if comments exist)
    if hasattr(model, 'comments'):
        first_response_times = []
        for item in qs:
            first_comment = Comment.objects.filter(workitem=item).order_by('created_at').first()
            if first_comment:
                delta = first_comment.created_at - item.created_at
                first_response_times.append(delta.total_seconds())
        if first_response_times:
            stats['avg_time_to_first_response_hours'] = round(sum(first_response_times) / len(first_response_times) / 3600, 2)
        else:
            stats['avg_time_to_first_response_hours'] = None

    # Average time in each status (if activity logs exist)
    if hasattr(model, 'activity_log'):
        status_times = defaultdict(list)
        for item in qs:
            logs = list(ActivityLog.objects.filter(workitem=item, activity_type='status_changed').order_by('created_at'))
            prev_time = item.created_at
            prev_status = item.status
            for log in logs:
                status_times[prev_status].append((log.created_at - prev_time).total_seconds())
                prev_time = log.created_at
                prev_status = log.description.split(' to ')[-1].replace('"', '')
            end_time = item.updated_at if getattr(item, 'status', None) in ['resolved', 'closed'] else now
            status_times[prev_status].append((end_time - prev_time).total_seconds())
        stats['avg_time_in_status_hours'] = {status: round(sum(times)/len(times)/3600, 2) for status, times in status_times.items() if times}

        # Reopened
        reopened = 0
        for item in qs:
            logs = ActivityLog.objects.filter(workitem=item, activity_type='status_changed').order_by('created_at')
            statuses = [log.description.split(' to ')[-1].replace('"', '') for log in logs]
            if statuses.count('resolved') > 1 or statuses.count('closed') > 1:
                reopened += 1
        stats['reopened'] = reopened

    # Overdue (if deadline exists)
    if hasattr(model, 'deadline') and hasattr(model, 'status'):
        stats['overdue'] = qs.filter(deadline__lt=now, status__in=['open', 'in-progress']).count()

    # Longest open (top 10 by age)
    if hasattr(model, 'status') and hasattr(model, 'created_at'):
        open_items = qs.filter(status__in=['open', 'in-progress']).order_by('created_at')[:10]
        stats['longest_open'] = [
            {
                'id': str(item.id),
                'title': item.title,
                'created_at': item.created_at,
                'status': item.status,
                'assigned_user': item.assigned_user.username if hasattr(item, 'assigned_user') and item.assigned_user else None
            }
            for item in open_items
        ]

    # SLA compliance: % resolved within 3 days
    if hasattr(model, 'status') and hasattr(model, 'created_at') and hasattr(model, 'updated_at'):
        sla_days = 3
        resolved = qs.filter(status='resolved', updated_at__isnull=False)
        if resolved.exists():
            within_sla = resolved.filter(updated_at__lte=F('created_at') + timedelta(days=sla_days)).count()
            stats['sla_compliance_percent'] = round(100 * within_sla / resolved.count(), 2)
        else:
            stats['sla_compliance_percent'] = None

        # Average resolution time
        if resolved.exists():
            avg_resolution = resolved.annotate(
                resolution_time=ExpressionWrapper(F('updated_at') - F('created_at'), output_field=DurationField())
            ).aggregate(avg=Avg('resolution_time'))
            stats['average_resolution_time_days'] = round(avg_resolution['avg'].total_seconds() / 86400, 2) if avg_resolution['avg'] else None
        else:
            stats['average_resolution_time_days'] = None

    return stats


def get_all_workitem_statistics(tenant):
    # Auto-discover all WorkItem subclasses
    subclasses = WorkItem.__subclasses__()
    stats = {}
    for subclass in subclasses:
        stats[subclass.__name__.lower()] = get_workitem_statistics(subclass, tenant)
    return stats 