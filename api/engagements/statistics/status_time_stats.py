from collections import defaultdict

def get_avg_time_in_status(qs, ActivityLog, now):
    status_times = defaultdict(list)
    for item in qs:
        logs = list(ActivityLog.objects.filter(work_item=item, activity_type='status_changed').order_by('created_at'))
        prev_time = item.created_at
        prev_status = item.status
        for log in logs:
            status_times[prev_status].append((log.created_at - prev_time).total_seconds())
            prev_time = log.created_at
            prev_status = log.description.split(' to ')[-1].replace('"', '')
        end_time = item.updated_at if getattr(item, 'status', None) in ['resolved', 'closed'] else now
        status_times[prev_status].append((end_time - prev_time).total_seconds())
    return {status: round(sum(times)/len(times)/3600, 2) for status, times in status_times.items() if times}

def get_reopened_count(qs, ActivityLog):
    reopened = 0
    for item in qs:
        logs = ActivityLog.objects.filter(work_item=item, activity_type='status_changed').order_by('created_at')
        statuses = [log.description.split(' to ')[-1].replace('"', '') for log in logs]
        if statuses.count('resolved') > 1 or statuses.count('closed') > 1:
            reopened += 1
    return reopened 