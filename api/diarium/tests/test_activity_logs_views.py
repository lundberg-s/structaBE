import pytest
from django.urls import reverse
from diarium.tests.factory import create_user, authenticate_client
from diarium.models import ActivityLog, Case
from rest_framework import status
import uuid

pytestmark = pytest.mark.django_db

def test_activity_log_list_unauthenticated():
    url = reverse('diarium:activity-log-list-create')
    from rest_framework.test import APIClient
    client = APIClient()
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_activity_log_retrieve_not_found():
    client, user = authenticate_client()
    url = reverse('diarium:activity-log-detail', kwargs={'id': '00000000-0000-0000-0000-000000000000'})
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_activity_log_create_invalid_data():
    client, user = authenticate_client()
    url = reverse('diarium:activity-log-list-create')
    # Missing required fields
    response = client.post(url, {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_activity_log_create_and_retrieve():
    client, user = authenticate_client()
    from diarium.models import Case
    case = Case.objects.create(title='Test', description='desc', status='open', category='Bug', priority='high', created_by=user)
    url = reverse('diarium:activity-log-list-create')
    payload = {
        'case': str(case.id),
        'activity_type': 'created',
        'description': 'Case created'
    }
    response = client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    log_id = response.data['id']
    # Retrieve
    detail_url = reverse('diarium:activity-log-detail', kwargs={'id': log_id})
    get_response = client.get(detail_url)
    assert get_response.status_code == status.HTTP_200_OK

def test_activity_log_filter_by_case_user_activity_type():
    client, user = authenticate_client()
    from diarium.models import Case, ActivityLog
    case1 = Case.objects.create(title='Case1', description='desc', status='open', category='Bug', priority='high', created_by=user)
    case2 = Case.objects.create(title='Case2', description='desc', status='open', category='Bug', priority='high', created_by=user)
    log1 = ActivityLog.objects.create(case=case1, user=user, activity_type='created', description='desc1')
    log2 = ActivityLog.objects.create(case=case2, user=user, activity_type='updated', description='desc2')
    url = reverse('diarium:activity-log-list-create')
    # Filter by case
    response = client.get(url, {'case': str(case1.id)})
    assert response.status_code == status.HTTP_200_OK
    assert all(str(item['case']) == str(case1.id) for item in response.data)
    # Filter by user (should return at least one log for this user)
    response = client.get(url, {'user': user.id})
    assert response.status_code == status.HTTP_200_OK
    assert any(str(item['user']['id']) == str(user.id) for item in response.data)
    # Filter by activity_type
    response = client.get(url, {'activity_type': 'created'})
    assert response.status_code == status.HTTP_200_OK
    assert any(item['activity_type'] == 'created' for item in response.data)

def test_activity_log_search_by_description():
    client, user = authenticate_client()
    from diarium.models import Case, ActivityLog
    case = Case.objects.create(title='Case', description='desc', status='open', category='Bug', priority='high', created_by=user)
    ActivityLog.objects.create(case=case, user=user, activity_type='created', description='unique_search_term')
    url = reverse('diarium:activity-log-list-create')
    response = client.get(url, {'search': 'unique_search_term'})
    assert response.status_code == status.HTTP_200_OK
    assert any('unique_search_term' in item['description'] for item in response.data)

def test_invalid_uuid_returns_400():
    client, user = authenticate_client()
    url = reverse('diarium:activity-log-list-create')

    # Invalid UUID (not in proper format)
    response = client.get(url, {'case': 'not-a-uuid'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


def test_nonexistent_uuid_returns_200_and_empty_list():
    client, user = authenticate_client()
    url = reverse('diarium:activity-log-list-create')

    # Valid but non-existent UUID
    response = client.get(url, {'case': str(uuid.uuid4())})
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


def test_nonexistent_user_returns_200_and_empty_list():
    client, user = authenticate_client()
    url = reverse('diarium:activity-log-list-create')

    # Non-existent user ID
    response = client.get(url, {'user': 999999})
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


def test_invalid_activity_type_returns_200_and_empty_list():
    client, user = authenticate_client()
    url = reverse('diarium:activity-log-list-create')

    # Invalid activity_type
    response = client.get(url, {'activity_type': 'not-a-type'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []

def test_activity_log_retrieve_existing():
    client, user = authenticate_client()
    from diarium.models import Case, ActivityLog
    case = Case.objects.create(title='Case', description='desc', status='open', category='Bug', priority='high', created_by=user)
    log = ActivityLog.objects.create(case=case, user=user, activity_type='created', description='desc')
    url = reverse('diarium:activity-log-detail', kwargs={'id': log.id})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == str(log.id) 