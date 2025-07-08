def get_avg_time_to_first_response(qs, Comment):
    first_response_times = []
    for item in qs:
        first_comment = Comment.objects.filter(work_item=item).order_by('created_at').first()
        if first_comment:
            delta = first_comment.created_at - item.created_at
            first_response_times.append(delta.total_seconds())
    if first_response_times:
        return round(sum(first_response_times) / len(first_response_times) / 3600, 2)
    return None 