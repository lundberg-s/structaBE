from django.db import models


class CustomRoleQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get custom roles for a specific tenant."""
        return self.filter(tenant=tenant)

    def by_key(self, key):
        """Get custom role by key."""
        return self.filter(key=key)


class PartnerQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get partners for a specific tenant."""
        return self.filter(tenant=tenant)


class PersonQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get persons for a specific tenant."""
        return self.filter(tenant=tenant)

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
    def by_tenant(self, tenant):
        """Get organizations for a specific tenant."""
        return self.filter(tenant=tenant)

    def by_name(self, name):
        """Get organizations by name."""
        return self.filter(name__icontains=name)

    def by_organization_number(self, org_number):
        """Get organization by organization number."""
        return self.filter(organization_number=org_number)


class RelationReferenceQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get relation references for a specific tenant."""
        return self.filter(tenant=tenant)

    def by_type(self, ref_type):
        """Get relation references by type."""
        return self.filter(type=ref_type)

    def by_partner(self, partner):
        """Get relation references for a specific partner."""
        return self.filter(partner=partner)

    def by_work_item(self, work_item):
        """Get relation references for a specific work item."""
        return self.filter(workitem=work_item)


class RelationQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get relations for a specific tenant."""
        return self.filter(tenant=tenant)

    def by_type(self, relation_type):
        """Get relations by type."""
        return self.filter(relation_type=relation_type)

    def by_partner(self, partner):
        """Get all relations involving a specific partner."""
        from relations.models import RelationReference

        refs = RelationReference.objects.filter(partner=partner)
        return self.filter(
            models.Q(source__in=refs) | models.Q(target__in=refs)
        )

    def by_work_item(self, work_item):
        """Get all relations involving a specific work item."""
        from relations.models import RelationReference

        refs = RelationReference.objects.filter(workitem=work_item)
        return self.filter(
            models.Q(source__in=refs) | models.Q(target__in=refs)
        )


class RoleQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get roles for a specific tenant."""
        return self.filter(tenant=tenant)

    def by_system_role(self, system_role):
        """Get roles by system role."""
        return self.filter(system_role=system_role)

    def by_custom_role(self, custom_role):
        """Get roles by custom role."""
        return self.filter(custom_role=custom_role)

    def by_partner(self, partner):
        """Get all roles for a specific partner."""
        from relations.models import RelationReference

        refs = RelationReference.objects.filter(partner=partner)
        return self.filter(target__in=refs)

    def by_work_item(self, work_item):
        """Get all roles for a specific work item."""
        from relations.models import RelationReference

        refs = RelationReference.objects.filter(workitem=work_item)
        return self.filter(target__in=refs)
