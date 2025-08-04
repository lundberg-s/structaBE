from django.contrib.auth import get_user_model
from relations.models import Relation, Assignment
from relations.choices import RelationObjectType

User = get_user_model()


class RelationFactory:
    @classmethod
    def create_partner_to_partner(cls, tenant, created_by, source_partner, target_partner, role, **kwargs):
        return cls.create(
            tenant=tenant,
            created_by=created_by,
            source_type=RelationObjectType.PERSON,
            source_partner=source_partner,
            source_workitem=None,
            target_type=RelationObjectType.ORGANIZATION,
            target_partner=target_partner,
            target_workitem=None,
            role=role,
            **kwargs,
        )

    @classmethod
    def create_partner_to_workitem(cls, tenant, created_by, source_partner, target_workitem, role, **kwargs):
        return cls.create(
            tenant=tenant,
            created_by=created_by,
            source_type=RelationObjectType.PERSON,
            source_partner=source_partner,
            source_workitem=None,
            target_type=RelationObjectType.WORKITEM,
            target_partner=None,
            target_workitem=target_workitem,
            role=role,
            **kwargs,
        )

    @classmethod
    def create_workitem_to_workitem(cls, tenant, created_by, source_workitem, target_workitem, role, **kwargs):
        return cls.create(
            tenant=tenant,
            created_by=created_by,
            source_type=RelationObjectType.WORKITEM,
            source_partner=None,
            source_workitem=source_workitem,
            target_type=RelationObjectType.WORKITEM,
            target_partner=None,
            target_workitem=target_workitem,
            role=role,
            **kwargs,
        )


class AssignmentFactory:
    @classmethod
    def create(cls, tenant, created_by, relation, **kwargs):
        return Assignment.objects.create(
            tenant=tenant,
            created_by=created_by.id if created_by else None,
            relation=relation,
            **kwargs,
        )
