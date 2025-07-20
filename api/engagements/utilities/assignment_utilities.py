from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from engagements.models import Assignment
from users.models import User

def update_work_item_assignments(work_item, new_user_ids, assigned_by_user):
    current_user_ids = set(
        work_item.assignments.values_list('user_id', flat=True)
    )
    new_user_ids = set(new_user_ids)

    users_to_remove = current_user_ids - new_user_ids
    users_to_add = new_user_ids - current_user_ids

    if users_to_remove:
        _remove_assignments(work_item, users_to_remove)

    if users_to_add:
        _add_assignments(work_item, users_to_add, assigned_by_user)

def _remove_assignments(work_item, user_ids):
    Assignment.objects.filter(work_item=work_item, user_id__in=user_ids).delete()

def _add_assignments(work_item, user_ids, assigned_by_user):
    tenant = work_item.tenant

    valid_users = User.objects.filter(id__in=user_ids, tenant=tenant)
    found_user_ids = set(user.id for user in valid_users)
    missing_ids = user_ids - found_user_ids

    if missing_ids:
        raise ValidationError(f"User(s) with ID(s) {missing_ids} not found or not in the same tenant.")

    assignments = [
        Assignment(work_item=work_item, user=user, assigned_by=assigned_by_user)
        for user in valid_users
    ]
    Assignment.objects.bulk_create(assignments)
