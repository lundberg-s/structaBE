import uuid
from relations.models import Person, Organization, RelationReference, CustomRole, Role, Relation
from relations.choices import RelationObjectType, SystemRole
from core.models import Tenant
from django.contrib.auth import get_user_model

User = get_user_model()

def create_person(tenant, first_name='John', last_name='Doe', **kwargs):
    return Person.objects.create(tenant=tenant, first_name=first_name, last_name=last_name, **kwargs)

def create_organization(tenant, name='Test Org', organization_number=None, **kwargs):
    return Organization.objects.create(tenant=tenant, name=name, organization_number=organization_number, **kwargs)

def create_relation_reference_for_person(person):
    return RelationReference.objects.create(type=RelationObjectType.PERSON, partner=person)

def create_relation_reference_for_organization(org):
    return RelationReference.objects.create(type=RelationObjectType.ORGANIZATION, partner=org)

def create_custom_role(tenant, key=None, label=None):
    if key is None:
        key = f'custom_{uuid.uuid4().hex[:6]}'
    if label is None:
        label = f'Custom Role {uuid.uuid4().hex[:4]}'
    return CustomRole.objects.create(tenant=tenant, key=key, label=label)

def create_role(tenant, target, system_role=None, custom_role=None):
    return Role.objects.create(
        tenant=tenant,
        target=target,
        system_role=system_role,
        custom_role=custom_role
    )

def create_relation(tenant, source, target, relation_type=None):
    return Relation.objects.create(
        tenant=tenant,
        source=source,
        target=target,
        relation_type=relation_type
    ) 