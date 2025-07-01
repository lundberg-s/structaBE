import pytest
from django.urls import reverse
from diarium.tests.factory import create_user, authenticate_client, create_case
from diarium.models import Case
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_case_list_unauthenticated():
    url = reverse('diarium:case-list')
    from rest_framework.test import APIClient
    client = APIClient()
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_case_list_authenticated():
    client, user = authenticate_client()
    create_case(user, title='Case 1')
    create_case(user, title='Case 2')
    url = reverse('diarium:case-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2

def test_case_retrieve():
    client, user = authenticate_client()
    case = create_case(user)
    url = reverse('diarium:case-detail', kwargs={'id': case.id})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == str(case.id)

def test_case_retrieve_not_found():
    client, user = authenticate_client()
    url = reverse('diarium:case-detail', kwargs={'id': '00000000-0000-0000-0000-000000000000'})
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_case_create_invalid_data():
    client, user = authenticate_client()
    url = reverse('diarium:case-list')
    response = client.post(url, {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_case_create():
    client, user = authenticate_client()
    url = reverse('diarium:case-list')
    payload = {
        'title': 'New Case',
        'description': 'desc',
        'status': 'open',
        'category': 'Bug',
        'priority': 'high'
    }
    response = client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == 'New Case'

def test_case_update():
    client, user = authenticate_client()
    case = create_case(user)
    url = reverse('diarium:case-detail', kwargs={'id': case.id})
    payload = {
        'title': 'Updated',
        'description': 'desc',
        'status': 'in-progress',
        'category': 'Feature',
        'priority': 'medium'
    }
    response = client.put(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'Updated'

def test_case_patch():
    client, user = authenticate_client()
    case = create_case(user)
    url = reverse('diarium:case-detail', kwargs={'id': case.id})
    payload = {'title': 'Patched'}
    response = client.patch(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'Patched'

def test_case_delete():
    client, user = authenticate_client()
    case = create_case(user)
    url = reverse('diarium:case-detail', kwargs={'id': case.id})
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Confirm deleted
    get_response = client.get(url)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_case_delete_not_found():
    client, user = authenticate_client()
    url = reverse('diarium:case-detail', kwargs={'id': '00000000-0000-0000-0000-000000000000'})
    response = client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_case_update_invalid_data():
    client, user = authenticate_client()
    case = create_case(user)
    url = reverse('diarium:case-detail', kwargs={'id': case.id})
    payload = {'title': ''}  # title required
    response = client.put(url, payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_case_patch_invalid_data():
    client, user = authenticate_client()
    case = create_case(user)
    url = reverse('diarium:case-detail', kwargs={'id': case.id})
    payload = {'status': 'not-a-valid-status'}
    response = client.patch(url, payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_case_update_status_and_assignment_creates_activity_logs():
    client, user = authenticate_client()
    assigned_user = create_user(username='assigned', email='assigned@example.com')
    case = create_case(user, status='open')
    url = reverse('diarium:case-detail', kwargs={'id': case.id})
    # Change status and assign user
    payload = {
        'title': case.title,
        'description': case.description,
        'status': 'in-progress',
        'category': case.category,
        'priority': case.priority,
        'assigned_user': assigned_user.id
    }
    response = client.put(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    # Change status again and unassign
    payload['status'] = 'resolved'
    payload['assigned_user'] = None
    response2 = client.put(url, payload, format='json')
    assert response2.status_code == status.HTTP_200_OK
    # Check activity logs
    from diarium.models import ActivityLog
    logs = ActivityLog.objects.filter(case=case)
    activity_types = [log.activity_type for log in logs]
    assert 'status_changed' in activity_types
    assert 'assigned' in activity_types
    # Only assert 'updated' if no status or assignment change
    # (simulate a title change only)
    payload['status'] = 'resolved'
    payload['assigned_user'] = None
    payload['title'] = 'Updated Title'
    response3 = client.put(url, payload, format='json')
    assert response3.status_code == status.HTTP_200_OK
    logs = ActivityLog.objects.filter(case=case)
    activity_types = [log.activity_type for log in logs]
    assert 'updated' in activity_types

def test_case_delete_creates_activity_log(monkeypatch):
    client, user = authenticate_client()
    case = create_case(user)
    url = reverse('diarium:case-detail', kwargs={'id': case.id})
    from diarium.models import ActivityLog
    called = {}
    def fake_create(**kwargs):
        called['created'] = kwargs
        return ActivityLog(**kwargs)
    monkeypatch.setattr(ActivityLog.objects, 'create', fake_create)
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # The activity log for deletion should have been created before deletion
    assert 'created' in called
    assert called['created']['activity_type'] == 'deleted'
    assert called['created']['case'] is not None
    assert called['created']['case'].title == case.title 