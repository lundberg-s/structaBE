import uuid
from django.contrib.auth import get_user_model
from engagements.models import Ticket, Case, Job, Comment, Attachment, WorkItemStatus, WorkItemPriority, WorkItemCategory
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

# Global counter for generating unique ticket numbers in tests
_ticket_counter = 0

def create_ticket(tenant, created_by, status, category, priority, **kwargs):
    global _ticket_counter
    _ticket_counter += 1
    
    # Create ticket with a unique test-specific ticket number
    # This avoids conflicts with the model's auto-generation
    test_ticket_number = f"TEST{_ticket_counter:06d}"
    
    # Default values
    defaults = {
        'title': 'Test Ticket',
        'description': 'This is a test ticket',
        'ticket_number': test_ticket_number,  # Set the ticket number directly
    }
    
    # Update defaults with any provided kwargs
    defaults.update(kwargs)
    
    ticket = Ticket.objects.create(
        tenant=tenant,
        created_by=created_by,
        status=status,
        category=category,
        priority=priority,
        **defaults
    )
    
    return ticket

def create_case(tenant, created_by, status, category, priority, case_reference=None, **kwargs):
    if case_reference is None:
        case_reference = f'C-{uuid.uuid4().hex[:8]}'

    defaults = {
        'title': 'Test Case',
        'description': 'This is a test Case',
        'legal_area': 'Civil',
        'court_date': None,
        **kwargs
    }

    return Case.objects.create(
        tenant=tenant,
        created_by=created_by,
        status=status,
        category=category,
        priority=priority,
        case_reference=case_reference,
        **defaults
    )

def create_job(tenant, created_by, status, category, priority, job_code=None, estimated_hours=10.5):
    if job_code is None:
        job_code = f'J-{uuid.uuid4().hex[:8]}'

    defaults = {
        'title': 'Test Job',
        'description': 'This is a test job',
        'estimated_hours': 10.5,
    }
    return Job.objects.create(
        tenant=tenant,
        status=status,
        category=category,
        priority=priority,
        created_by=created_by,
        job_code=job_code,
        **defaults
    )

def create_comment(work_item, author, content='Test comment'):
    return Comment.objects.create(
        tenant=work_item.tenant,
        work_item=work_item,
        content=content,
        created_by=author
    )

def create_attachment(work_item, uploaded_by, filename='test.txt', content=b'test content'):
    file = SimpleUploadedFile(filename, content)
    return Attachment.objects.create(
        tenant=work_item.tenant,
        work_item=work_item,
        file=file,
        filename=filename,
        file_size=len(content),
        created_by=uploaded_by
    )

def create_default_status(tenant, label, created_by):
    return WorkItemStatus.objects.create(
        tenant=tenant,
        label=label,
        use_translation=False,
        is_active=True,
        sort_order=0,
        created_by=created_by,
    )

def create_default_priority(tenant, label, created_by):
    return WorkItemPriority.objects.create(
        tenant=tenant,
        label=label,
        use_translation=False,
        is_active=True,
        sort_order=0,
        created_by=created_by,
    )

def create_default_category(tenant, label, created_by):
    return WorkItemCategory.objects.create(
        tenant=tenant,
        label=label,
        use_translation=False,
        is_active=True,
        sort_order=0,
        created_by=created_by,
    )