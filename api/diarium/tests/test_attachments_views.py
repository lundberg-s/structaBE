import pytest
from django.urls import reverse
from diarium.tests.factory import create_user, authenticate_client, create_case
from diarium.models import Attachment
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

pytestmark = pytest.mark.django_db

def test_attachment_list_unauthenticated():
    url = reverse('diarium:attachment-list-create')
    from rest_framework.test import APIClient
    client = APIClient()
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_attachment_retrieve_not_found():
    client, user = authenticate_client()
    url = reverse('diarium:attachment-detail', kwargs={'id': '00000000-0000-0000-0000-000000000000'})
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_attachment_create_invalid_data():
    client, user = authenticate_client()
    url = reverse('diarium:attachment-list-create')
    response = client.post(url, {}, format='multipart')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_attachment_upload_and_retrieve():
    client, user = authenticate_client()
    case = create_case(user)
    url = reverse('diarium:attachment-list-create')
    file = SimpleUploadedFile('test.txt', b'hello world', content_type='text/plain')
    payload = {
        'file': file,
        'filename': 'test.txt',
        'file_size': 11,
        'case': str(case.id)
    }
    response = client.post(url, payload, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED
    att_id = response.data['id']
    # Retrieve
    detail_url = reverse('diarium:attachment-detail', kwargs={'id': att_id})
    get_response = client.get(detail_url)
    assert get_response.status_code == status.HTTP_200_OK

def test_attachment_update_and_delete():
    client, user = authenticate_client()
    case = create_case(user)
    url = reverse('diarium:attachment-list-create')
    file = SimpleUploadedFile('test.txt', b'hello world', content_type='text/plain')
    payload = {
        'file': file,
        'filename': 'test.txt',
        'file_size': 11,
        'case': str(case.id)
    }
    response = client.post(url, payload, format='multipart')
    att_id = response.data['id']
    detail_url = reverse('diarium:attachment-detail', kwargs={'id': att_id})
    # Update (PUT) with multipart and file
    new_file = SimpleUploadedFile('updated.txt', b'updated content', content_type='text/plain')
    update_payload = {
        'file': new_file,
        'filename': 'updated.txt',
        'file_size': 15,
        'case': str(case.id)
    }
    put_response = client.put(detail_url, update_payload, format='multipart')
    assert put_response.status_code in (status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_204_NO_CONTENT)
    # Patch (partial update)
    patch_payload = {
        'filename': 'patched.txt'
    }
    patch_response = client.patch(detail_url, patch_payload, format='json')
    assert patch_response.status_code in (status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_204_NO_CONTENT)
    # Delete
    del_response = client.delete(detail_url)
    assert del_response.status_code == status.HTTP_204_NO_CONTENT
    # Confirm deleted
    get_response = client.get(detail_url)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND 