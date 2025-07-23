from django.db import models


class CustomRoleQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get custom roles for a specific tenant."""
        return self.filter(tenant=tenant)

    def by_key(self, key):
        """Get custom role by key."""
        return self.filter(key=key)


class PartnerQuerySet(models.QuerySet):
    def with_details(self):
        """Preload all related objects for better performance."""
        return self.select_related("person", "organization")

    def by_tenant(self, tenant):
        """Get partners for a specific tenant with optimized queries."""
        return self.filter(tenant=tenant).with_details()

    def customers(self, tenant):
        """Get all customers for a tenant with optimized queries."""
        return self.filter(tenant=tenant).select_related("person", "organization")

    def vendors(self, tenant):
        """Get all vendors for a tenant with optimized queries."""
        return self.filter(tenant=tenant).select_related("person", "organization")

    def by_work_item(self, work_item):
        """Get all partners involved in a work item with optimized queries."""
        from relations.models import RelationReference

        refs = RelationReference.objects.filter(workitem=work_item).select_related(
            "partner__person", "partner__organization"
        )
        return self.filter(id__in=[ref.partner.id for ref in refs])

    def with_relations(self, tenant):
        """Get partners with their relations preloaded for better performance."""
        return self.filter(tenant=tenant).prefetch_related(
            "relation_sources__target__partner", "relation_targets__source__partner"
        )

    def with_roles(self, tenant):
        """Get partners with their roles preloaded for better performance."""
        return self.filter(tenant=tenant).prefetch_related(
            "relation_sources__roles", "relation_targets__roles"
        )

    def with_work_items(self, tenant):
        """Get partners with their work items preloaded for better performance."""
        return self.filter(tenant=tenant).prefetch_related(
            "relation_sources__workitem", "relation_targets__workitem"
        )

    def with_contact_info(self, tenant):
        """Get partners with contact information preloaded."""
        return self.filter(tenant=tenant).select_related("person", "organization")

    def get_roles(self):
        """Get all roles for this partner through RelationReference."""
        from relations.models import RelationReference, Role
        refs = RelationReference.objects.filter(partner=self)
        return Role.objects.filter(target__in=refs)
        

    def get_partner_roles(self, partner):
        """Get all roles for a specific partner through RelationReference."""
        from relations.models import RelationReference, Role

        refs = RelationReference.objects.filter(partner=partner)
        return Role.objects.filter(target__in=refs)

    def get_partner_relations(self, partner):
        """Get all relations where a specific partner is involved."""
        from relations.models import RelationReference, Relation

        refs = RelationReference.objects.filter(partner=partner)
        return Relation.objects.filter(
            models.Q(source__in=refs) | models.Q(target__in=refs)
        )

    def get_partner_work_items(self, partner):
        """Get all work items a specific partner is involved in through relations."""
        from engagements.models import WorkItem

        return WorkItem.objects.filter(
            relation_targets__source__partner=partner
        ).distinct()

    def get_real_instance(self, partner):
        """Get the actual Person or Organization instance."""
        if hasattr(partner, 'person'):
            return partner.person
        if hasattr(partner, 'organization'):
            return partner.organization
        return partner

    def get_contact_info(self, partner):
        """Get contact information for this partner."""
        real_instance = self.get_real_instance(partner)
        if hasattr(real_instance, 'email'):
            return {
                'email': real_instance.email,
                'phone': getattr(real_instance, 'phone', None),
            }
        return {}


class PersonQuerySet(models.QuerySet):
    def with_details(self):
        """Preload all related objects for better performance."""
        return self.select_related("person")

    def by_tenant(self, tenant):
        """Get persons for a specific tenant with optimized queries."""
        return self.filter(tenant=tenant).with_details()

    def by_name(self, first_name=None, last_name=None):
        """Get persons by name."""
        queryset = self
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        return queryset

    def by_email(self, email):
        """Get person by email."""
        return self.filter(email=email)


class OrganizationQuerySet(models.QuerySet):
    def with_details(self):
        """Preload all related objects for better performance."""
        return self.select_related("organization")

    def by_tenant(self, tenant):
        """Get organizations for a specific tenant with optimized queries."""
        return self.filter(tenant=tenant).with_details()

    def by_name(self, name):
        """Get organizations by name."""
        return self.filter(name__icontains=name)

    def by_organization_number(self, org_number):
        """Get organization by organization number."""
        return self.filter(organization_number=org_number)


class RelationReferenceQuerySet(models.QuerySet):
    def with_details(self):
        """Preload all related objects for better performance."""
        return self.select_related(
            "partner__person", "partner__organization", "workitem"
        )

    def by_tenant(self, tenant):
        """Get relation references for a specific tenant with optimized queries."""
        return self.filter(tenant=tenant).with_details()

    def by_type(self, ref_type):
        """Get relation references by type."""
        return self.filter(type=ref_type).with_details()

    def by_partner(self, partner):
        """Get relation references for a specific partner."""
        return self.filter(partner=partner).with_details()

    def by_work_item(self, work_item):
        """Get relation references for a specific work item."""
        return self.filter(workitem=work_item).with_details()

    def get_object(self, ref):
        """Get the actual object referenced by this RelationReference."""
        from relations.utilities.validation_helpers import get_real_instance
        if ref.partner:
            return get_real_instance(ref.partner)
        if ref.workitem:
            return get_real_instance(ref.workitem)
        return None

    def validate_tenant(self, ref, tenant):
        """Validate tenant consistency for a relation reference."""
        from relations.utilities.validation_helpers import validate_tenant_consistency
        obj = self.get_object(ref)
        if obj:
            validate_tenant_consistency(tenant, obj)

    def validate_type_matches_instance(self, ref):
        """Validate that the type matches the FK subclass."""
        from relations.utilities.validation_helpers import get_real_instance
        from relations.models import Person, Organization
        
        if ref.partner:
            real_instance = get_real_instance(ref.partner)
            type_mapping = {Person: "person", Organization: "organization"}
            # This validation logic should be in the mixin, but we're calling it from queryset
            return real_instance, type_mapping
        return None, None

    def get_string_representation(self, ref):
        """Get string representation without database queries."""
        if ref.partner:
            return str(ref.partner)
        if ref.workitem:
            return str(ref.workitem)
        return str(ref.id)


class RelationQuerySet(models.QuerySet):
    def with_details(self):
        """Preload all related objects for better performance."""
        return self.select_related(
            "source__partner__person",
            "source__partner__organization",
            "source__workitem",
            "target__partner__person",
            "target__partner__organization",
            "target__workitem",
        )

    def by_tenant(self, tenant):
        """Get relations for a specific tenant with optimized queries."""
        return self.filter(tenant=tenant).with_details()

    def by_type(self, relation_type):
        """Get relations by type with optimized queries."""
        return self.filter(relation_type=relation_type).with_details()

    def by_partner(self, partner):
        """Get all relations involving a specific partner."""
        from relations.models import RelationReference

        refs = RelationReference.objects.filter(partner=partner)
        return self.filter(
            models.Q(source__in=refs) | models.Q(target__in=refs)
        ).with_details()

    def by_work_item(self, work_item):
        """Get all relations involving a specific work item."""
        from relations.models import RelationReference

        refs = RelationReference.objects.filter(workitem=work_item)
        return self.filter(
            models.Q(source__in=refs) | models.Q(target__in=refs)
        ).with_details()

    def validate_tenant_consistency(self, relation, tenant):
        """Validate tenant consistency for a relation."""
        from relations.models import RelationReference
        from relations.utilities.validation_helpers import validate_tenant_consistency
        source_obj = RelationReference.objects.get_object(relation.source)
        target_obj = RelationReference.objects.get_object(relation.target)
        validate_tenant_consistency(tenant, source_obj, target_obj)

    def get_string_representation(self, relation):
        from relations.models import RelationReference
        """Get string representation without database queries."""
        source_str = RelationReference.objects.get_string_representation(relation.source)
        target_str = RelationReference.objects.get_string_representation(relation.target)
        return f"{source_str} → {target_str} ({relation.relation_type})"


class RoleQuerySet(models.QuerySet):
    def with_details(self):
        """Preload all related objects for better performance."""
        return self.select_related(
            "target__partner__person",
            "target__partner__organization",
            "target__workitem",
            "custom_role",
        )

    def by_tenant(self, tenant):
        """Get roles for a specific tenant with optimized queries."""
        return self.filter(tenant=tenant).with_details()

    def by_system_role(self, system_role):
        """Get roles by system role with optimized queries."""
        return self.filter(system_role=system_role).with_details()

    def by_custom_role(self, custom_role):
        """Get roles by custom role with optimized queries."""
        return self.filter(custom_role=custom_role).with_details()

    def by_partner(self, partner):
        """Get all roles for a specific partner."""
        from relations.models import RelationReference

        refs = RelationReference.objects.filter(partner=partner)
        return self.filter(target__in=refs).with_details()

    def by_work_item(self, work_item):
        """Get all roles for a specific work item."""
        from relations.models import RelationReference

        refs = RelationReference.objects.filter(workitem=work_item)
        return self.filter(target__in=refs).with_details()
