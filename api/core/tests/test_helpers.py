from core.tests.factories import TenantFactory, RoleFactory
from django.test import TestCase
from engagements.tests.test_constants import WorkItemType


class CoreTestHelper(TestCase):
    def setUp(self):
        super().setUp()
        self.tenant = self.create_tenant()

    def create_tenant(self, work_item_type=None):
        work_item_type = work_item_type or WorkItemType.TICKET

        tenant = TenantFactory.create(work_item_type=work_item_type)
        return tenant

    def create_role(
        self, key=None, label=None, is_system=False, tenant=None, created_by=None
    ):
        role = RoleFactory.get_or_create(
            key=key,
            label=label,
            is_system=is_system,
            tenant=tenant,
            created_by=created_by,
        )
        return role
