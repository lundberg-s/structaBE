from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from relations.models import Assignment, Relation
from relations.choices import RelationType, RelationObjectType
from users.models import User

def create_or_get_assignment_relation(person, work_item, tenant, created_by):
    """
    Create or get a relation for an assignment.
    
    Args:
        person: The Person (source partner)
        work_item: The WorkItem (target)
        tenant: The tenant
        created_by: The user creating the assignment
        
    Returns:
        Relation: The existing or newly created relation
    """
    from core.models import Role
    
    # Get or create the assigned_to role
    role, _ = Role.objects.get_or_create(
        tenant=tenant,
        key=RelationType.ASSIGNED_TO,
        defaults={
            'label': 'Assigned To',
            'is_system': False
        }
    )
    
    relation, created = Relation.objects.get_or_create(
        tenant=tenant,
        source_partner=person,
        source_type=RelationObjectType.PERSON,
        target_workitem=work_item,
        target_type=RelationObjectType.WORKITEM,
        role=role,
        defaults={
            'created_by': created_by,
            'updated_by': created_by,
        }
    )
    return relation

def update_work_item_assignments(work_item, new_user_ids, created_by_user):
    # Get current assigned user IDs from the assigned_to property (which returns a list)
    current_user_ids = set(user.id for user in work_item.assigned_to)
    new_user_ids = set(new_user_ids)

    users_to_remove = current_user_ids - new_user_ids
    users_to_add = new_user_ids - current_user_ids

    if users_to_remove:
        _remove_assignments(work_item, users_to_remove)

    if users_to_add:
        _add_assignments(work_item, users_to_add, created_by_user)

def _remove_assignments(work_item, user_ids):
    from core.models import Role
    
    # Get the assigned_to role
    try:
        role = Role.objects.get(
            tenant=work_item.tenant,
            key=RelationType.ASSIGNED_TO
        )
    except Role.DoesNotExist:
        # If role doesn't exist, there are no assignments to remove
        return
    
    # Find relations where this work item is the target and role is "assigned_to"
    # Get the person IDs for the users
    from relations.models import Person
    person_ids = Person.objects.filter(user__id__in=user_ids).values_list('id', flat=True)
    
    relations = Relation.objects.filter(
        target_workitem=work_item,
        target_type=RelationObjectType.WORKITEM,
        role=role,
        source_partner_id__in=person_ids
    )
    
    # Delete assignments for these relations
    Assignment.objects.filter(relation__in=relations).delete()

def _add_assignments(work_item, user_ids, created_by_user):
    tenant = work_item.tenant

    valid_users = User.objects.filter(id__in=user_ids, tenant=tenant)
    found_user_ids = set(user.id for user in valid_users)
    missing_ids = set(user_ids) - found_user_ids

    if missing_ids:
        raise ValidationError(f"User(s) with ID(s) {missing_ids} not found or not in the same tenant.")

    # Get or create relations for each user
    assignments = []
    for user in valid_users:
        # Get the person associated with this user through the partner relationship
        try:
            person = user.partner.person
        except (ObjectDoesNotExist, AttributeError):
            raise ValidationError(f"User {user.id} does not have an associated Person record.")
        
        # Get or create the relation using the utility function
        relation = create_or_get_assignment_relation(person, work_item, tenant, created_by_user)
        
        # Create assignment for this relation
        assignment = Assignment(
            tenant=tenant,
            relation=relation,
            created_by=created_by_user,
            updated_by=created_by_user
        )
        assignments.append(assignment)
    
    Assignment.objects.bulk_create(assignments)
