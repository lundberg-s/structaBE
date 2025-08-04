from django.contrib.auth import get_user_model
from partners.models import Person, Organization

User = get_user_model()


class PersonFactory:
    @classmethod
    def create(cls, tenant, created_by, first_name="John", last_name="Doe", **kwargs):
        return Person.objects.create(
            tenant=tenant,
            first_name=first_name,
            last_name=last_name,
            created_by=created_by.id if created_by else None,
            **kwargs,
        )


class OrganizationFactory:
    @classmethod
    def create(cls, tenant, created_by, name="Test Org", organization_number=None, **kwargs):
        return Organization.objects.create(
            tenant=tenant,
            name=name,
            organization_number=organization_number,
            created_by=created_by.id if created_by else None,
            **kwargs,
        )

