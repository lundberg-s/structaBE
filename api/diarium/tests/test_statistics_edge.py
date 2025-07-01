import pytest
from diarium.statistics_utils import get_case_statistics
from diarium.tests.factory import create_user, create_case
from diarium.models import Case
from django.utils import timezone

pytestmark = pytest.mark.django_db

def test_statistics_with_no_cases():
    stats = get_case_statistics()
    assert stats['total_cases'] == 0
    assert stats['cases_by_status'] == {}
    assert stats['cases_by_priority'] == {}
    assert stats['cases_by_category'] == {}
    assert stats['cases_created_per_month'] == {}
    assert stats['cases_resolved_per_month'] == {}
    assert stats['cases_created_per_week'] == {}
    assert stats['cases_resolved_per_week'] == {}
    assert stats['open_cases_at_month_end'] == {}
    assert stats['avg_cases_per_user'] == 0
    assert stats['cases_resolved_per_user'] == {}
    assert stats['unassigned_cases'] == 0
    assert stats['avg_time_to_first_response_hours'] is None
    assert stats['avg_time_in_status_hours'] == {}
    assert stats['cases_reopened'] == 0
    assert stats['overdue_cases'] == 0
    assert stats['longest_open_cases'] == []
    assert stats['sla_compliance_percent'] is None
    assert stats['average_resolution_time_days'] is None
    assert stats['cases_by_assigned_user'] == {}
    assert stats['cases_by_created_user'] == {}

def test_statistics_with_no_comments():
    user = create_user()
    create_case(user, status='open')
    stats = get_case_statistics()
    assert stats['avg_time_to_first_response_hours'] is None

def test_statistics_with_no_resolved_cases():
    user = create_user()
    create_case(user, status='open')
    stats = get_case_statistics()
    assert stats['average_resolution_time_days'] is None
    assert stats['sla_compliance_percent'] is None 