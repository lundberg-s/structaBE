import pytest
from diarium.models import Attachment, Case, Comment, ActivityLog
from diarium.tests.factory import create_user, create_case
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

pytestmark = pytest.mark.django_db

def test_attachment_save_sets_mime_type():
    user = create_user()
    case = create_case(user)
    file = SimpleUploadedFile('test.txt', b'hello world', content_type='text/plain')
    attachment = Attachment(
        case=case,
        file=file,
        filename='test.txt',
        file_size=11,
        uploaded_by=user
    )
    attachment.save()
    assert attachment.mime_type == 'text/plain'

def test_attachment_save_no_file():
    user = create_user()
    case = create_case(user)
    attachment = Attachment(
        case=case,
        filename='nofile.txt',
        file_size=0,
        uploaded_by=user
    )
    # Should not raise error even if file is None
    attachment.save()
    assert attachment.mime_type is None or attachment.mime_type == ''

def test_comment_str():
    user = create_user()
    case = create_case(user)
    comment = Comment.objects.create(case=case, author=user, content='Test')
    assert str(comment) == f"Comment by {user.username} on {case.title}"

def test_activitylog_str():
    user = create_user()
    case = create_case(user)
    log = ActivityLog.objects.create(case=case, user=user, activity_type='created', description='desc')
    assert str(log) == f"created by {user.username} on {case.title}" 