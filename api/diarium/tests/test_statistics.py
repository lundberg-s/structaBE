from django.urls import reverse
from rest_framework import status
from diarium.tests.factory import create_user, create_case, authenticate_client
from diarium.statistics_utils import get_case_statistics
from diarium.models import Case, Comment
import pytest
from datetime import timedelta
from django.utils import timezone

pytestmark = pytest.mark.django_db

def test_statistics_endpoint_returns_all_metrics():
    client, user = authenticate_client()
    # Create cases with different statuses, priorities, categories, deadlines
    case1 = create_case(user, status='open', priority='high', category='Bug')
    case2 = create_case(user, status='resolved', priority='medium', category='Feature', updated_at=timezone.now())
    case3 = create_case(user, status='in-progress', priority='urgent', category='Support')
    # Add a comment to test first response
    Comment.objects.create(case=case1, author=user, content='First response')
    # Set deadlines for overdue
    case3.deadline = timezone.now() - timedelta(days=1)
    case3.save()
    url = reverse('diarium:case-statistics')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Check for all expected keys
    expected_keys = [
        'total_cases', 'cases_by_status', 'cases_by_priority', 'cases_by_category',
        'cases_created_per_month', 'cases_resolved_per_month', 'cases_created_per_week',
        'cases_resolved_per_week', 'open_cases_at_month_end', 'avg_cases_per_user',
        'cases_resolved_per_user', 'unassigned_cases', 'avg_time_to_first_response_hours',
        'avg_time_in_status_hours', 'cases_reopened', 'overdue_cases', 'longest_open_cases',
        'sla_compliance_percent', 'average_resolution_time_days', 'cases_by_assigned_user',
        'cases_by_created_user'
    ]
    for key in expected_keys:
        assert key in data

def test_get_case_statistics_utility():
    user = create_user()
    case = create_case(user, status='resolved', priority='high', category='Bug', updated_at=timezone.now())
    stats = get_case_statistics()
    assert isinstance(stats, dict)
    assert stats['total_cases'] >= 1
    assert 'cases_by_status' in stats
    assert 'cases_by_priority' in stats
    assert 'cases_by_category' in stats
    assert 'cases_created_per_month' in stats
    assert 'cases_resolved_per_month' in stats
    assert 'cases_created_per_week' in stats
    assert 'cases_resolved_per_week' in stats
    assert 'open_cases_at_month_end' in stats
    assert 'avg_cases_per_user' in stats
    assert 'cases_resolved_per_user' in stats
    assert 'unassigned_cases' in stats
    assert 'avg_time_to_first_response_hours' in stats
    assert 'avg_time_in_status_hours' in stats
    assert 'cases_reopened' in stats
    assert 'overdue_cases' in stats
    assert 'longest_open_cases' in stats
    assert 'sla_compliance_percent' in stats
    assert 'average_resolution_time_days' in stats
    assert 'cases_by_assigned_user' in stats
    assert 'cases_by_created_user' in stats 