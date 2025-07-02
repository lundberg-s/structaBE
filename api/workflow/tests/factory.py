import uuid
from django.contrib.auth import get_user_model
from workflow.models import Tenant, Ticket, Comment, Attachment
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

def create_tenant(name='TestTenant'):
    tenant = Tenant.objects.create(name=name)
    tenant.workitem_type = 'ticket'
    tenant.save()
    return tenant

def create_user(tenant, username='testuser', password='testpass', email=None):
    if email is None:
        email = f"{username}@example.com"
    user = User.objects.create_user(username=username, email=email, password=password, tenant=tenant)
    return user

def create_workitem(tenant, user, **kwargs):
    """
    Create a WorkItem of the correct subclass (Ticket, Case, or Job) based on the tenant's workitem_type.
    """
    workitem_type = getattr(tenant, 'workitem_type', 'ticket')
    base_kwargs = {
        'tenant': tenant,
        'created_by': user,
        'assigned_user': kwargs.get('assigned_user', None),
        'title': kwargs.get('title', 'Test WorkItem'),
        'description': kwargs.get('description', 'Test description'),
        'status': kwargs.get('status', 'open'),
        'category': kwargs.get('category', 'general'),
        'priority': kwargs.get('priority', 'medium'),
        'deadline': kwargs.get('deadline', None),
    }
    if workitem_type == 'ticket':
        ticket_kwargs = {
            'ticket_number': kwargs.get('ticket_number', uuid.uuid4().hex),
            'reported_by': kwargs.get('reported_by', user.username if hasattr(user, 'username') else 'reporter'),
            'urgency': kwargs.get('urgency', 'medium'),
        }
        base_kwargs.update(ticket_kwargs)
        return Ticket.objects.create(**base_kwargs)
    elif workitem_type == 'case':
        case_kwargs = {
            'case_reference': kwargs.get('case_reference', uuid.uuid4().hex),
            'legal_area': kwargs.get('legal_area', 'General'),
            'court_date': kwargs.get('court_date', None),
        }
        base_kwargs.update(case_kwargs)
        from workflow.models import Case
        return Case.objects.create(**base_kwargs)
    elif workitem_type == 'job':
        job_kwargs = {
            'job_code': kwargs.get('job_code', uuid.uuid4().hex),
            'assigned_team': kwargs.get('assigned_team', 'Team A'),
            'estimated_hours': kwargs.get('estimated_hours', 1.0),
        }
        base_kwargs.update(job_kwargs)
        from workflow.models import Job
        return Job.objects.create(**base_kwargs)
    else:
        raise ValueError(f"Unknown workitem_type: {workitem_type}")


def create_comment(ticket, author, content='Test comment'):
    return Comment.objects.create(
        tenant=ticket.tenant,
        workitem=ticket,
        author=author,
        content=content
    )

def create_attachment(ticket, uploaded_by, filename='test.txt', content=b'test content'):
    file = SimpleUploadedFile(filename, content)
    return Attachment.objects.create(
        tenant=ticket.tenant,
        workitem=ticket,
        file=file,
        filename=filename,
        file_size=len(content),
        uploaded_by=uploaded_by
    ) 