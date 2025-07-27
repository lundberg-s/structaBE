import uuid
from django.contrib.auth import get_user_model
from engagements.models import Ticket, Case, Job, Comment, Attachment
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

# Global counter for generating unique ticket numbers in tests
_ticket_counter = 0

def create_ticket(tenant, created_by, **kwargs):
    global _ticket_counter
    _ticket_counter += 1
    
    # Create ticket with a unique test-specific ticket number
    # This avoids conflicts with the model's auto-generation
    test_ticket_number = f"TEST{_ticket_counter:06d}"
    
    # Default values
    defaults = {
        'title': 'Test Ticket',
        'description': 'This is a test ticket',
        'status': 'open',
        'category': 'ticket',
        'priority': 'medium',
        'ticket_number': test_ticket_number,  # Set the ticket number directly
    }
    
    # Update defaults with any provided kwargs
    defaults.update(kwargs)
    
    ticket = Ticket.objects.create(
        tenant=tenant,
        created_by=created_by,
        **defaults
    )
    
    return ticket

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

def create_job(tenant, created_by, job_code=None, estimated_hours=10.5):
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
        estimated_hours=estimated_hours,
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

