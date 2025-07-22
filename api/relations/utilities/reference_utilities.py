def get_or_create_reference(obj):
    from relations.models import RelationReference, Person, Organization
    from engagements.models import WorkItem
    from relations.choices import RelationObjectType

    if isinstance(obj, Person):
        return RelationReference.objects.get_or_create(type=RelationObjectType.PERSON, person=obj)[0]
    elif isinstance(obj, Organization):
        return RelationReference.objects.get_or_create(type=RelationObjectType.ORGANIZATION, organization=obj)[0]
    elif isinstance(obj, WorkItem):
        return RelationReference.objects.get_or_create(type=RelationObjectType.WORKITEM, workitem=obj)[0]
    raise ValueError(f"Unsupported reference object type: {type(obj)}")
