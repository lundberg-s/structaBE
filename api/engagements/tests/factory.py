
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from engagements.models import (
    Ticket,
    Case,
    Job,
    Comment,
    Attachment,
    WorkItemStatus,
    WorkItemPriority,
    WorkItemCategory,
)

User = get_user_model()


class WorkItemStatusFactory:
    @classmethod
    def create(cls, tenant, created_by, label="Open"):
        return WorkItemStatus.objects.create(
            tenant=tenant,
            label=label,
            created_by=created_by.id if created_by else None,
        )


class WorkItemCategoryFactory:
    @classmethod
    def create(cls, tenant, created_by, label="Support"):
        return WorkItemCategory.objects.create(
            tenant=tenant,
            label=label,
            created_by=created_by.id if created_by else None,
        )


class WorkItemPriorityFactory:
    @classmethod
    def create(cls, tenant, created_by, label="Medium"):
        return WorkItemPriority.objects.create(
            tenant=tenant,
            label=label,
            created_by=created_by.id if created_by else None,
        )


class TicketFactory:
    _counter = 0

    @classmethod
    def _get_ticket_number(cls):
        cls._counter += 1
        return f"T-{cls._counter:04d}"

    @classmethod
    def create(cls, tenant, created_by, **kwargs):
        status = kwargs.pop("status", WorkItemStatusFactory.create(tenant, created_by))
        category = kwargs.pop("category", WorkItemCategoryFactory.create(tenant, created_by))
        priority = kwargs.pop("priority", WorkItemPriorityFactory.create(tenant, created_by))

        return Ticket.objects.create(
            tenant=tenant,
            created_by=created_by.id if created_by else None,
            title=kwargs.get("title", "Test Ticket"),
            description=kwargs.get("description", "This is a test ticket"),
            ticket_number=kwargs.get("ticket_number", cls._get_ticket_number()),
            status=status,
            category=category,
            priority=priority,
        )


class CaseFactory:
    @classmethod
    def _generate_reference(cls):
        return f"C-{uuid.uuid4().hex[:8]}"

    @classmethod
    def create(cls, tenant, created_by, **kwargs):
        status = kwargs.pop("status", WorkItemStatusFactory.create(tenant, created_by))
        category = kwargs.pop("category", WorkItemCategoryFactory.create(tenant, created_by))
        priority = kwargs.pop("priority", WorkItemPriorityFactory.create(tenant, created_by))

        return Case.objects.create(
            tenant=tenant,
            created_by=created_by.id if created_by else None,
            title=kwargs.get("title", "Test Case"),
            description=kwargs.get("description", "This is a test case"),
            case_reference=kwargs.get("case_reference", cls._generate_reference()),
            legal_area=kwargs.get("legal_area", "Civil"),
            court_date=kwargs.get("court_date", None),
            status=status,
            category=category,
            priority=priority,
        )


class JobFactory:
    @classmethod
    def _generate_job_code(cls):
        return f"J-{uuid.uuid4().hex[:8]}"

    @classmethod
    def create(cls, tenant, created_by, **kwargs):
        status = kwargs.pop("status", WorkItemStatusFactory.create(tenant, created_by))
        category = kwargs.pop("category", WorkItemCategoryFactory.create(tenant, created_by))
        priority = kwargs.pop("priority", WorkItemPriorityFactory.create(tenant, created_by))

        return Job.objects.create(
            tenant=tenant,
            created_by=created_by.id if created_by else None,
            title=kwargs.get("title", "Test Job"),
            description=kwargs.get("description", "This is a test job"),
            job_code=kwargs.get("job_code", cls._generate_job_code()),
            estimated_hours=kwargs.get("estimated_hours", 10.5),
            status=status,
            category=category,
            priority=priority,
        )


class CommentFactory:
    @classmethod
    def create(cls, tenant, created_by, work_item, author=None, content="Test comment"):
        return Comment.objects.create(
            tenant=tenant,
            work_item=work_item,
            content=content,
            created_by=created_by.id,
        )


class AttachmentFactory:
    @classmethod
    def create(
        cls,
        tenant,
        created_by,
        work_item,
        uploaded_by=None,
        filename="test.txt",
        content=b"test content",
    ):
        file = SimpleUploadedFile(filename, content)
        return Attachment.objects.create(
            tenant=tenant,
            work_item=work_item,
            file=file,
            filename=filename,
            file_size=len(content),
            created_by=created_by.id,
        )
