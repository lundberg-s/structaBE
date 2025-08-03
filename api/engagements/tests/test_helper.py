from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.enums import SystemRole
from core.models import Tenant
from core.tests.factory import TenantFactory, RoleFactory
from users.tests.factory import UserFactory
from relations.tests.factory import PersonFactory
from engagements.tests.factory import (
    TicketFactory,
    CaseFactory,
    JobFactory,
    CommentFactory,
    AttachmentFactory,
    WorkItemStatusFactory,
    WorkItemCategoryFactory,
    WorkItemPriorityFactory,
)
from engagements.models import Ticket, Case, Job, Comment, Attachment
from .test_constants import TestData, WorkItemType, QueryParams

User = get_user_model()


class EngagementsTestHelper(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tenant = self.create_tenant()
        self.user = self.create_user(tenant=self.tenant)
        self.token = self.authenticate_user()
        self.authenticate_client()

    def create_tenant(self, work_item_type=None):
        work_item_type = work_item_type or WorkItemType.TICKET
        
        tenant = TenantFactory.create(work_item_type=work_item_type)
        return tenant

    def create_user(self, email=None, password=None, tenant=None):
        email = email or TestData.DEFAULT_USER_EMAIL
        password = password or TestData.DEFAULT_USER_PASSWORD
        tenant = tenant or self.tenant

        user = UserFactory.create(
            tenant=tenant,
            username=email.split("@")[0],
            password=password,
            email=email,
        )

        person = PersonFactory.create(
            tenant=tenant,
            first_name=TestData.DEFAULT_USER_FIRST_NAME,
            last_name=TestData.DEFAULT_USER_LAST_NAME,
        )
        role = RoleFactory.get_or_create(
            created_by=user,
            key=SystemRole.TENANT_EMPLOYEE.value,
            label=SystemRole.labels()[SystemRole.TENANT_EMPLOYEE.value],
            is_system=True,
        )
        person.role = role
        person.save()

        user.partner = person
        user.save()
        return user

    def create_tickets(self, amount=1, tenant=None, user=None):
        tenant = tenant or self.tenant
        user = user or self.user
        return [
            TicketFactory.create(
                tenant=tenant, created_by=user, title=f"Test Ticket {i}"
            )
            for i in range(amount)
        ]

    def get_ticket(self, id):
        return Ticket.objects.get(id=id)

    def filter_tickets(self, **kwargs):
        return Ticket.objects.filter(**kwargs)

    def create_cases(self, amount=1, tenant=None, user=None):
        tenant = tenant or self.tenant
        user = user or self.user
        return [
            CaseFactory.create(tenant=tenant, created_by=user, title=f"Test Case {i}")
            for i in range(amount)
        ]

    def get_case(self, id):
        return Case.objects.get(id=id)

    def filter_cases(self, **kwargs):
        return Case.objects.filter(**kwargs)


    def create_jobs(self, amount=1, tenant=None, user=None):
        tenant = tenant or self.tenant
        user = user or self.user
        return [
            JobFactory.create(tenant=tenant, created_by=user, title=f"Test Job {i}")
            for i in range(amount)
        ]

    def get_job(self, id):
        return Job.objects.get(id=id)

    def filter_jobs(self, **kwargs):
        return Job.objects.filter(**kwargs)

    def create_comments(self, work_item, amount=1, tenant=None, user=None):
        tenant = tenant or self.tenant
        user = user or self.user
        return [
            CommentFactory.create(
                tenant=tenant,
                created_by=user,
                work_item=work_item,
                content=f"Test Comment {i}",
            )
            for i in range(amount)
        ]

    def get_comment(self, id):
        return Comment.objects.get(id=id)

    def filter_comments(self, **kwargs):
        return Comment.objects.filter(**kwargs)

    def create_attachments(self, work_item, amount=1, tenant=None, user=None):
        tenant = tenant or self.tenant
        user = user or self.user
        return [
            AttachmentFactory.create(
                tenant=tenant,
                created_by=user,
                work_item=work_item,
                filename=f"test_file_{i}.txt",
                content=f"test content {i}".encode(),
            )
            for i in range(amount)
        ]

    def get_attachment(self, id):
        return Attachment.objects.get(id=id)

    def filter_attachments(self, **kwargs):
        return Attachment.objects.filter(**kwargs)

    def create_work_item_statuses(self, amount=1, tenant=None, user=None):
        tenant = tenant or self.tenant
        user = user or self.user
        statuses = ["Open", "In Progress", "Closed", "Pending", "Cancelled"]
        return [
            WorkItemStatusFactory.create(
                tenant=tenant, 
                created_by=user, 
                label=statuses[i % len(statuses)]
            )
            for i in range(amount)
        ]

    def create_work_item_categories(self, amount=1, tenant=None, user=None):
        tenant = tenant or self.tenant
        user = user or self.user
        categories = ["Support", "Bug", "Feature", "Maintenance", "Documentation"]
        return [
            WorkItemCategoryFactory.create(
                tenant=tenant, 
                created_by=user, 
                label=categories[i % len(categories)]
            )
            for i in range(amount)
        ]

    def create_work_item_priorities(self, amount=1, tenant=None, user=None):
        tenant = tenant or self.tenant
        user = user or self.user
        priorities = ["Low", "Medium", "High", "Critical", "Urgent"]
        return [
            WorkItemPriorityFactory.create(
                tenant=tenant, 
                created_by=user, 
                label=priorities[i % len(priorities)]
            )
            for i in range(amount)
        ]

    def create_tmp_file(
        self,
        filename="test_file.txt",
        content=b"test content",
        content_type="text/plain",
    ):
        return SimpleUploadedFile(
            name=filename, 
            content=content, 
            content_type=content_type
        )

    def get_work_item_data(self, **kwargs):
        """Get work item data for testing."""
        status = self.create_work_item_statuses(amount=1)[0]
        category = self.create_work_item_categories(amount=1)[0]
        priority = self.create_work_item_priorities(amount=1)[0]
        
        default_data = {
            "title": "Test work item",
            "description": "Test Description",
            "status": status.id,
            "category": category.id,
            "priority": priority.id,
        }
        default_data.update(kwargs)
        return default_data

    def user_login(self, email, password):
        payload = {
            "email": email,
            "password": password,
        }
        response = self.client.post(reverse("login"), payload)
        return response

    def authenticate_user(self, email=None, password=None):
        email = email or TestData.DEFAULT_USER_EMAIL
        password = password or TestData.DEFAULT_USER_PASSWORD
        
        response = self.client.post(
            reverse("login"),
            {"email": email, "password": password},
            format="json",
        )
        assert response.status_code == 200, "Login failed during setup"
        return response.cookies.get("access_token").value

    def build_search_url(self, base_url, search_term):
        """Helper method to build a URL with search parameter."""
        return f"{base_url}?{QueryParams.SEARCH}={search_term}"

    def build_filter_url(self, base_url, **filters):
        """Helper method to build a URL with filter parameters."""
        params = []
        for key, value in filters.items():
            params.append(f"{key}={value}")
        return f"{base_url}?{'&'.join(params)}"

    def authenticate_client(self):
        """Authenticate the client for API requests."""
        self.client.cookies["access_token"] = self.token
