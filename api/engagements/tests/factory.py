import uuid
from django.contrib.auth import get_user_model
from engagements.models import Ticket, Case, Job, Comment, Attachment, Assignment
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

def create_ticket(tenant, created_by):
    return Ticket.objects.create(
        tenant=tenant,
        title='Test Ticket',
        description='This is a test ticket',
        status='open',
        category='ticket',
        priority='medium',
        created_by=created_by,
    )

def create_case(tenant, created_by, case_reference=None, **kwargs):
    if case_reference is None:
        case_reference = f'C-{uuid.uuid4().hex[:8]}'
    return Case.objects.create(
        tenant=tenant,
        created_by=created_by,
        case_reference=case_reference,
        title='Test Case',
        description='This is a test Case',
        status='open',
        category='case',
        priority='medium',
        legal_area='Civil',
        court_date=None,
        **kwargs
    )

def create_job(tenant, created_by, job_code=None, assigned_team='Team A', estimated_hours=10.5):
    if job_code is None:
        job_code = f'J-{uuid.uuid4().hex[:8]}'
    return Job.objects.create(
        tenant=tenant,
        title='Test Job',
        description='This is a test job',
        status='open',
        category='job',
        priority='medium',
        created_by=created_by,
        job_code=job_code,
        assigned_team=assigned_team,
        estimated_hours=estimated_hours,
    )

def create_comment(work_item, author, content='Test comment'):
    return Comment.objects.create(
        tenant=work_item.tenant,
        work_item=work_item,
        author=author,
        content=content
    )

def create_attachment(work_item, uploaded_by, filename='test.txt', content=b'test content'):
    file = SimpleUploadedFile(filename, content)
    return Attachment.objects.create(
        tenant=work_item.tenant,
        work_item=work_item,
        file=file,
        filename=filename,
        file_size=len(content),
        uploaded_by=uploaded_by
    )

def create_assignment(work_item, user, assigned_by=None):
    if assigned_by is None:
        assigned_by = user
    return Assignment.objects.create(
        work_item=work_item,
        user=user,
        assigned_by=assigned_by
    )