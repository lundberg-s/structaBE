from user.models import Person, Organization
from django.contrib.contenttypes.models import ContentType

def get_partner_content_type_and_obj(partner_id):
    """
    Given a UUID, return (ContentType, partner_obj) for Person or Organization, or (None, None) if not found.
    """
    for model_class in [Person, Organization]:
        try:
            obj = model_class.objects.get(id=partner_id)
            return ContentType.objects.get_for_model(model_class), obj
        except model_class.DoesNotExist:
            continue
    return None, None 