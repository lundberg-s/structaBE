from django.contrib import admin
from django import forms
from relations.models import Partner, Person, Organization, Role, RelationReference, Relation
from relations.choices import RelationType

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'partner_type', 'partner_name', 'partner_details', 'tenant_access', 'roles_count', 'user_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('id', 'person__first_name', 'person__last_name', 'person__email', 'organization__name', 'organization__organization_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def tenant_access(self, obj):
        """Show tenant access - partner now has direct tenant relationship"""
        if hasattr(obj, 'tenant') and obj.tenant:
            return f"{obj.tenant}"
        return 'No tenant access'
    tenant_access.short_description = 'Tenant'
    
    def partner_type(self, obj):
        """Show whether this is a Person or Organization"""
        if hasattr(obj, 'person'):
            return 'Person'
        elif hasattr(obj, 'organization'):
            return 'Organization'
        return 'Unknown'
    partner_type.short_description = 'Type'
    partner_type.admin_order_field = 'person__first_name'  # For sorting
    
    def partner_name(self, obj):
        """Show the name of the Person or Organization"""
        if hasattr(obj, 'person') and obj.person:
            return f"{obj.person.first_name} {obj.person.last_name}"
        elif hasattr(obj, 'organization') and obj.organization:
            return obj.organization.name
        return 'N/A'
    partner_name.short_description = 'Name'
    partner_name.admin_order_field = 'person__first_name'
    
    def partner_details(self, obj):
        """Show additional details like email for Person or org number for Organization"""
        if hasattr(obj, 'person') and obj.person:
            details = []
            if obj.person.email:
                details.append(f"Email: {obj.person.email}")
            if obj.person.phone:
                details.append(f"Phone: {obj.person.phone}")
            return " | ".join(details) if details else "No contact info"
        elif hasattr(obj, 'organization') and obj.organization:
            if obj.organization.organization_number:
                return f"Org #: {obj.organization.organization_number}"
            return "No org number"
        return 'N/A'
    partner_details.short_description = 'Details'
    
    def roles_count(self, obj):
        """Show how many roles this partner has"""
        count = obj.get_roles().count()
        return count if count > 0 else '-'
    roles_count.short_description = 'Roles'
    roles_count.admin_order_field = 'roles__count'
    
    def user_count(self, obj):
        """Show if this partner has a user account"""
        if hasattr(obj, 'user'):
            return 'Yes' if obj.user else 'No'
        return 'N/A'
    user_count.short_description = 'Has User'

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'has_user', 'user_tenant', 'role', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('first_name', 'last_name')
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'
    
    def has_user(self, obj):
        return 'Yes' if hasattr(obj, 'user') and obj.user else 'No'
    has_user.short_description = 'Has User Account'
    
    def user_tenant(self, obj):
        """Show the tenant - person now has direct tenant relationship"""
        if hasattr(obj, 'tenant') and obj.tenant:
            return obj.tenant
        return 'No tenant access'
    user_tenant.short_description = 'Tenant'
    
    def role(self, obj):
        role = obj.get_roles().first()
        return role.get_role_type_display() if role else "-"
    role.short_description = 'Role'

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization_number', 'has_tenant', 'tenant', 'role', 'created_at')
    list_filter = ('created_at', 'updated_at', 'tenant')
    search_fields = ('name', 'organization_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)
    
    def get_queryset(self, request):
        """Optimize queryset to reduce database queries"""
        return super().get_queryset(request).select_related('tenant')
    
    def has_tenant(self, obj):
        return 'Yes' if hasattr(obj, 'tenant') and obj.tenant else 'No'
    has_tenant.short_description = 'Has Tenant'
    
    def role(self, obj):
        role = obj.get_roles().first()
        return role.get_role_type_display() if role else "-"
    role.short_description = 'Role'

class RoleAdminForm(forms.ModelForm):
    """Custom form for Role admin with better target selection"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'target' in self.fields:
            # Get all RelationReferences that have partners (not work items)
            target_choices = []
            
            # Add organizations
            organizations = Organization.objects.select_related('tenant').all()
            for org in organizations:
                ref, created = RelationReference.objects.get_or_create(
                    partner=org,
                    type='organization',
                    defaults={'type': 'organization'}
                )
                target_choices.append((ref.id, f"🏢 {org.name} (Organization)"))
            
            # Add persons
            persons = Person.objects.select_related('tenant').all()
            for person in persons:
                ref, created = RelationReference.objects.get_or_create(
                    partner=person,
                    type='person',
                    defaults={'type': 'person'}
                )
                target_choices.append((ref.id, f"👤 {person.first_name} {person.last_name} (Person)"))
            
            self.fields['target'].choices = [('', '---------')] + target_choices

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    form = RoleAdminForm
    list_display = ('id', 'target_name', 'target_type', 'get_role_display', 'tenant', 'created_at')
    list_filter = ('system_role', 'created_at', 'updated_at')
    search_fields = ('target__partner__person__first_name', 'target__partner__person__last_name', 'target__partner__organization__name', 'system_role')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Role Information', {
            'fields': ('target', 'system_role', 'custom_role', 'tenant'),
            'description': 'Assign roles to organizations or persons. The target dropdown will show all available organizations and persons with icons.'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def target_name(self, obj):
        """Show the name of the target (Person or Organization)"""
        if obj.target and obj.target.partner:
            partner = obj.target.partner
            if hasattr(partner, 'person'):
                return f"{partner.person.first_name} {partner.person.last_name}"
            elif hasattr(partner, 'organization'):
                return partner.organization.name
        return 'N/A'
    target_name.short_description = 'Target Name'
    
    def target_type(self, obj):
        """Show whether the target is a Person or Organization"""
        if obj.target and obj.target.partner:
            if hasattr(obj.target.partner, 'person'):
                return 'Person'
            elif hasattr(obj.target.partner, 'organization'):
                return 'Organization'
        return 'Unknown'
    target_type.short_description = 'Target Type'
    
    def tenant(self, obj):
        """Show the tenant"""
        return obj.tenant if obj.tenant else 'No tenant'
    tenant.short_description = 'Tenant'
    
    def get_role_display(self, obj):
        """Show the role type (system or custom)"""
        if obj.system_role:
            return f"System: {obj.get_system_role_display()}"
        elif obj.custom_role:
            return f"Custom: {obj.custom_role.label}"
        return "No role assigned"
    get_role_display.short_description = 'Role Type'


class RelationAdminForm(forms.ModelForm):
    """Custom form for Relation admin with better source/target selection"""
    
    # Class-level cache for choices to avoid repeated heavy operations
    _choices_cache = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only do heavy lifting on GET requests (form display)
        # Check if this is a GET request by looking for data and files
        is_get_request = not kwargs.get('data') and not kwargs.get('files')
        
        if is_get_request and self._choices_cache is None:
            self._setup_choices()
            # Cache the choices for future use
            self._choices_cache = {
                'source_choices': self.fields['source'].choices if 'source' in self.fields else [],
                'target_choices': self.fields['target'].choices if 'target' in self.fields else [],
                'relation_type_choices': self.fields['relation_type'].choices if 'relation_type' in self.fields else []
            }
        elif is_get_request and self._choices_cache:
            # Use cached choices
            if 'source' in self.fields:
                self.fields['source'].choices = self._choices_cache['source_choices']
            if 'target' in self.fields:
                self.fields['target'].choices = self._choices_cache['target_choices']
            if 'relation_type' in self.fields:
                self.fields['relation_type'].choices = self._choices_cache['relation_type_choices']
    
    def _setup_choices(self):
        """Setup choices for the form fields - only called on GET requests"""
        # Get all existing RelationReferences in one query
        existing_refs = RelationReference.objects.select_related(
            'partner__person', 
            'partner__organization', 
            'workitem'
        ).all()
        
        # Create a mapping for quick lookup
        ref_map = {}
        for ref in existing_refs:
            if ref.partner:
                if hasattr(ref.partner, 'person'):
                    ref_map[('person', ref.partner.id)] = ref
                elif hasattr(ref.partner, 'organization'):
                    ref_map[('organization', ref.partner.id)] = ref
            elif ref.workitem:
                ref_map[('workitem', ref.workitem.id)] = ref
        
        ref_choices = []
        
        # Add organizations with bulk creation
        organizations = Organization.objects.select_related('tenant').all()
        org_refs_to_create = []
        for org in organizations:
            key = ('organization', org.id)
            if key not in ref_map:
                org_refs_to_create.append(RelationReference(
                    partner=org,
                    type='organization'
                ))
            else:
                ref_choices.append((ref_map[key].id, f"🏢 {org.name} (Organization)"))
        
        # Bulk create organization references
        if org_refs_to_create:
            created_refs = RelationReference.objects.bulk_create(org_refs_to_create)
            for ref in created_refs:
                ref_choices.append((ref.id, f"🏢 {ref.partner.name} (Organization)"))
        
        # Add persons with bulk creation
        persons = Person.objects.select_related('tenant').all()
        person_refs_to_create = []
        for person in persons:
            key = ('person', person.id)
            if key not in ref_map:
                person_refs_to_create.append(RelationReference(
                    partner=person,
                    type='person'
                ))
            else:
                ref_choices.append((ref_map[key].id, f"👤 {person.first_name} {person.last_name} (Person)"))
        
        # Bulk create person references
        if person_refs_to_create:
            created_refs = RelationReference.objects.bulk_create(person_refs_to_create)
            for ref in created_refs:
                ref_choices.append((ref.id, f"👤 {ref.partner.first_name} {ref.partner.last_name} (Person)"))
        
        # Add work items with bulk creation
        from engagements.models import WorkItem
        work_items = WorkItem.objects.select_related('tenant').all()
        workitem_refs_to_create = []
        for work_item in work_items:
            key = ('workitem', work_item.id)
            if key not in ref_map:
                workitem_refs_to_create.append(RelationReference(
                    workitem=work_item,
                    type='workitem'
                ))
            else:
                ref_choices.append((ref_map[key].id, f"📋 {work_item.title} (WorkItem)"))
        
        # Bulk create work item references
        if workitem_refs_to_create:
            created_refs = RelationReference.objects.bulk_create(workitem_refs_to_create)
            for ref in created_refs:
                ref_choices.append((ref.id, f"📋 {ref.workitem.title} (WorkItem)"))
        
        # Set choices for both source and target fields
        if 'source' in self.fields:
            self.fields['source'].choices = [('', '---------')] + ref_choices
        if 'target' in self.fields:
            self.fields['target'].choices = [('', '---------')] + ref_choices
        
        # Set choices for relation_type field
        if 'relation_type' in self.fields:
            self.fields['relation_type'].choices = [('', '---------')] + list(RelationType.choices)
    
    def clean(self):
        """Custom validation to reduce queries"""
        cleaned_data = super().clean()
        
        # Validate that source and target are different
        source = cleaned_data.get('source')
        target = cleaned_data.get('target')
        
        if source and target and source == target:
            from django import forms
            raise forms.ValidationError("Source and target cannot be the same.")
        
        return cleaned_data
    
    @classmethod
    def clear_cache(cls):
        """Clear the choices cache - call this when data changes"""
        cls._choices_cache = None


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    form = RelationAdminForm
    list_display = ('id', 'source_display', 'relation_type', 'target_display', 'tenant', 'created_at')
    list_filter = ('relation_type', 'created_at', 'updated_at', 'tenant')
    search_fields = (
        'source__partner__person__first_name', 
        'source__partner__person__last_name', 
        'source__partner__organization__name',
        'target__partner__person__first_name', 
        'target__partner__person__last_name', 
        'target__partner__organization__name',
        'source__workitem__title',
        'target__workitem__title',
        'relation_type'
    )
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        """Optimize queryset to reduce database queries"""
        return super().get_queryset(request).select_related(
            'source__partner__person',
            'source__partner__organization',
            'source__workitem',
            'target__partner__person',
            'target__partner__organization',
            'target__workitem',
            'tenant'
        )
    
    def save_model(self, request, obj, form, change):
        """Optimize save to reduce queries"""
        if not change:  # Only for new objects
            # Set tenant from request user if not set
            if not obj.tenant and hasattr(request.user, 'tenant'):
                obj.tenant = request.user.tenant
        super().save_model(request, obj, form, change)
        
        # Clear the form cache after saving
        RelationAdminForm.clear_cache()
    
    fieldsets = (
        ('Relation Information', {
            'fields': ('source', 'target', 'relation_type', 'tenant'),
            'description': 'Create relationships between organizations, persons, and work items. The dropdowns will show all available entities with icons.'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def source_display(self, obj):
        """Show the source of the relation"""
        if obj.source and obj.source.partner:
            partner = obj.source.partner
            if hasattr(partner, 'person'):
                return f"👤 {partner.person.first_name} {partner.person.last_name}"
            elif hasattr(partner, 'organization'):
                return f"🏢 {partner.organization.name}"
        elif obj.source and obj.source.workitem:
            return f"📋 {obj.source.workitem.title}"
        return 'N/A'
    source_display.short_description = 'Source'
    
    def target_display(self, obj):
        """Show the target of the relation"""
        if obj.target and obj.target.partner:
            partner = obj.target.partner
            if hasattr(partner, 'person'):
                return f"👤 {partner.person.first_name} {partner.person.last_name}"
            elif hasattr(partner, 'organization'):
                return f"🏢 {partner.organization.name}"
        elif obj.target and obj.target.workitem:
            return f"📋 {obj.target.workitem.title}"
        return 'N/A'
    target_display.short_description = 'Target'


# Register your models here.
