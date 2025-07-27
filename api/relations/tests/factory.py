import uuid
from relations.models import Person, Organization, Role, Relation
from relations.choices import RelationObjectType, SystemRole
from core.models import Tenant
from django.contrib.auth import get_user_model

User = get_user_model()

def create_person(tenant, first_name='John', last_name='Doe', **kwargs):
    return Person.objects.create(tenant=tenant, first_name=first_name, last_name=last_name, **kwargs)

def create_organization(tenant, name='Test Org', organization_number=None, **kwargs):
    return Organization.objects.create(tenant=tenant, name=name, organization_number=organization_number, **kwargs)



def create_custom_role(tenant, key=None, label=None):
    if key is None:
        key = f'custom_{uuid.uuid4().hex[:6]}'
    if label is None:
        label = f'Custom Role {uuid.uuid4().hex[:4]}'
    return CustomRole.objects.create(tenant=tenant, key=key, label=label)

def create_role(tenant, label, is_system=False):
    return Role.objects.create(
        tenant=tenant,
        label=label,
        is_system=is_system
    )

def create_relation(tenant, source_partner, target_partner, role):
    return Relation.objects.create(
        tenant=tenant,
        source_partner=source_partner,
        target_partner=target_partner,
        source_type='person' if hasattr(source_partner, 'person') else 'organization',
        target_type='person' if hasattr(target_partner, 'person') else 'organization',
        role=role
    ) 