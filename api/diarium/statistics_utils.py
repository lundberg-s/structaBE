from diarium.models import Case, ActivityLog
from django.db.models import Count, Avg, F, ExpressionWrapper, DateTimeField, Q, Min, Max, DurationField
from django.utils import timezone
from collections import defaultdict
from datetime import timedelta, datetime


def get_case_statistics():
    stats = {}
    now = timezone.now()

    # Total cases
    stats['total_cases'] = Case.objects.count()

    # Cases by status
    stats['cases_by_status'] = dict(Case.objects.values_list('status').annotate(count=Count('id')))

    # Cases by priority
    stats['cases_by_priority'] = dict(Case.objects.values_list('priority').annotate(count=Count('id')))

    # Cases by category
    stats['cases_by_category'] = dict(Case.objects.values_list('category').annotate(count=Count('id')))

    # Cases created per month (last 12 months)
    cases_per_month = (
        Case.objects.extra(select={'month': "strftime('%%Y-%%m', created_at)"})
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    stats['cases_created_per_month'] = {item['month']: item['count'] for item in cases_per_month}

    # Cases resolved per month (last 12 months)
    resolved_cases = (
        Case.objects.filter(status='resolved')
        .extra(select={'month': "strftime('%%Y-%%m', updated_at)"})
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    stats['cases_resolved_per_month'] = {item['month']: item['count'] for item in resolved_cases}

    # Cases created per week (last 12 weeks)
    cases_per_week = (
        Case.objects.extra(select={'week': "strftime('%%Y-%%W', created_at)"})
        .values('week')
        .annotate(count=Count('id'))
        .order_by('week')
    )
    stats['cases_created_per_week'] = {item['week']: item['count'] for item in cases_per_week}

    # Cases resolved per week (last 12 weeks)
    resolved_per_week = (
        Case.objects.filter(status='resolved')
        .extra(select={'week': "strftime('%%Y-%%W', updated_at)"})
        .values('week')
        .annotate(count=Count('id'))
        .order_by('week')
    )
    stats['cases_resolved_per_week'] = {item['week']: item['count'] for item in resolved_per_week}

    # Open cases at end of each month (last 12 months)
    open_cases_month = {}
    for item in cases_per_month:
        month = item['month']
        year, m = map(int, month.split('-'))
        last_day = datetime(year, m, 28) + timedelta(days=4)
        last_day = last_day - timedelta(days=last_day.day)
        count = Case.objects.filter(created_at__lte=last_day, status__in=['open', 'in-progress']).count()
        open_cases_month[month] = count
    stats['open_cases_at_month_end'] = open_cases_month

    # Average number of cases assigned per user (current)
    assigned_counts = (
        Case.objects.values('assigned_user__username')
        .annotate(count=Count('id'))
        .exclude(assigned_user__isnull=True)
    )
    if assigned_counts:
        stats['avg_cases_per_user'] = sum([item['count'] for item in assigned_counts]) / max(len(assigned_counts), 1)
    else:
        stats['avg_cases_per_user'] = 0

    # Cases resolved per user (per month)
    resolved_per_user = (
        Case.objects.filter(status='resolved')
        .values('assigned_user__username')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    stats['cases_resolved_per_user'] = {item['assigned_user__username'] or 'Unassigned': item['count'] for item in resolved_per_user}

    # Cases with no assigned user
    stats['unassigned_cases'] = Case.objects.filter(assigned_user__isnull=True).count()

    # Average time to first response (if you track comments or activity logs)
    # We'll use the first comment as first response
    first_response_times = []
    for case in Case.objects.all():
        first_comment = case.comments.order_by('created_at').first()
        if first_comment:
            delta = first_comment.created_at - case.created_at
            first_response_times.append(delta.total_seconds())
    if first_response_times:
        stats['avg_time_to_first_response_hours'] = round(sum(first_response_times) / len(first_response_times) / 3600, 2)
    else:
        stats['avg_time_to_first_response_hours'] = None

    # Average time in each status (open, in-progress, resolved, closed)
    # This requires activity logs to track status changes
    status_times = defaultdict(list)
    for case in Case.objects.all():
        logs = list(case.activity_log.filter(activity_type='status_changed').order_by('created_at'))
        prev_time = case.created_at
        prev_status = case.status
        for log in logs:
            status_times[prev_status].append((log.created_at - prev_time).total_seconds())
            prev_time = log.created_at
            prev_status = log.description.split(' to ')[-1].replace('"', '')
        # Time from last status change to now or resolution
        end_time = case.updated_at if case.status in ['resolved', 'closed'] else now
        status_times[prev_status].append((end_time - prev_time).total_seconds())
    stats['avg_time_in_status_hours'] = {status: round(sum(times)/len(times)/3600, 2) for status, times in status_times.items() if times}

    # Cases reopened after being resolved/closed
    reopened = 0
    for case in Case.objects.all():
        logs = case.activity_log.filter(activity_type='status_changed').order_by('created_at')
        statuses = [log.description.split(' to ')[-1].replace('"', '') for log in logs]
        if statuses.count('resolved') > 1 or statuses.count('closed') > 1:
            reopened += 1
    stats['cases_reopened'] = reopened

    # Overdue cases (past deadline and not resolved/closed)
    stats['overdue_cases'] = Case.objects.filter(deadline__lt=now, status__in=['open', 'in-progress']).count()

    # Longest open cases (top 10 by age)
    open_cases = Case.objects.filter(status__in=['open', 'in-progress']).order_by('created_at')[:10]
    stats['longest_open_cases'] = [
        {
            'id': str(case.id),
            'title': case.title,
            'created_at': case.created_at,
            'status': case.status,
            'assigned_user': case.assigned_user.username if case.assigned_user else None
        }
        for case in open_cases
    ]

    # SLA compliance: % of cases resolved within 3 days
    sla_days = 3
    resolved = Case.objects.filter(status='resolved', updated_at__isnull=False)
    if resolved.exists():
        within_sla = resolved.filter(updated_at__lte=F('created_at') + timedelta(days=sla_days)).count()
        stats['sla_compliance_percent'] = round(100 * within_sla / resolved.count(), 2)
    else:
        stats['sla_compliance_percent'] = None

    # Average resolution time (for resolved cases)
    if resolved.exists():
        avg_resolution = resolved.annotate(
            resolution_time=ExpressionWrapper(F('updated_at') - F('created_at'), output_field=DurationField())
        ).aggregate(avg=Avg('resolution_time'))
        stats['average_resolution_time_days'] = round(avg_resolution['avg'].total_seconds() / 86400, 2) if avg_resolution['avg'] else None
    else:
        stats['average_resolution_time_days'] = None

    # Cases by assigned user (current)
    assigned = (
        Case.objects.values('assigned_user__username')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    stats['cases_by_assigned_user'] = {item['assigned_user__username'] or 'Unassigned': item['count'] for item in assigned}

    # Cases by created user (current)
    created = (
        Case.objects.values('created_by__username')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    stats['cases_by_created_user'] = {item['created_by__username']: item['count'] for item in created}

    return stats 