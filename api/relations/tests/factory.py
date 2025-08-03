import uuid
from partners.models import Person, Organization
from relations.models import Relation, Assignment
from core.models import Role
from relations.choices import RelationObjectType
from core.models import Tenant
from django.contrib.auth import get_user_model

User = get_user_model()


class PersonFactory:
    @classmethod
    def create(cls, tenant, first_name="John", last_name="Doe", **kwargs):
        return Person.objects.create(
            tenant=tenant, first_name=first_name, last_name=last_name, **kwargs
        )


def create_tenant(work_item_type="ticket"):
    return Tenant.objects.create(work_item_type=work_item_type)


def create_user(tenant, username=None, password="testpass", email=None, **kwargs):
    if username is None:
        username = f"testuser_{uuid.uuid4().hex[:8]}"
    if email is None:
        email = f"{username}_{uuid.uuid4().hex[:8]}@example.com"
    return User.objects.create_user(
        username=username, password=password, email=email, tenant=tenant, **kwargs
    )


def create_person(tenant, first_name="John", last_name="Doe", **kwargs):
    return Person.objects.create(
        tenant=tenant, first_name=first_name, last_name=last_name, **kwargs
    )


def create_organization(tenant, name="Test Org", organization_number=None, **kwargs):
    return Organization.objects.create(
        tenant=tenant, name=name, organization_number=organization_number, **kwargs
    )


def create_custom_role(tenant, key=None, label=None):
    if key is None:
        key = f"custom_{uuid.uuid4().hex[:6]}"
    if label is None:
        label = f"Custom Role {uuid.uuid4().hex[:4]}"
    return CustomRole.objects.create(tenant=tenant, key=key, label=label)


def create_role(tenant, key=None, label=None, is_system=False):
    if key is None:
        key = f"role_{uuid.uuid4().hex[:6]}"
    if label is None:
        label = f"Role {uuid.uuid4().hex[:4]}"
    return Role.objects.create(
        tenant=None if is_system else tenant, key=key, label=label, is_system=is_system
    )


def create_relation(tenant, source_partner, target_partner, role):
    return Relation.objects.create(
        tenant=tenant,
        source_partner=source_partner,
        target_partner=target_partner,
        source_type=(
            RelationObjectType.PERSON
            if isinstance(source_partner, Person)
            else RelationObjectType.ORGANIZATION
        ),
        target_type=(
            RelationObjectType.PERSON
            if isinstance(target_partner, Person)
            else RelationObjectType.ORGANIZATION
        ),
        role=role,
    )


def create_ticket(tenant, created_by, **kwargs):
    """Create a ticket for testing purposes"""
    from engagements.tests.factory import create_ticket as create_ticket_engagement

    return create_ticket_engagement(tenant, created_by, **kwargs)


def create_assignment(relation, created_by=None):
    """Create an assignment for testing purposes"""
    return Assignment.objects.create(
        relation=relation, tenant=relation.tenant, created_by=created_by
    )
