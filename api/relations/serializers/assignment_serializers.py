from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from relations.models import Assignment, Relation
from relations.choices import RelationType, RelationObjectType
from relations.utilities.assignment_utilities import create_or_get_assignment_relation
from users.serializers.user_serializers import UserWithPersonSerializer


class AssignmentNameOnlySerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='relation.source_partner.person.first_name')
    last_name = serializers.CharField(source='relation.source_partner.person.last_name')

    class Meta:
        model = Assignment
        fields = ['id', 'first_name', 'last_name']

class AssignmentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'user']

    def get_user(self, obj):
        if obj.relation.source_partner and hasattr(obj.relation.source_partner, 'person'):
            person = obj.relation.source_partner.person
            if hasattr(person, 'user'):
                return UserWithPersonSerializer(person.user).data
        return None


class AssignmentCreateSerializer(serializers.ModelSerializer):
    work_item = serializers.UUIDField(write_only=True)
    user = serializers.UUIDField(write_only=True)
    user_data = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'work_item', 'user', 'user_data', 'created_by', 'created_at']
        read_only_fields = ['id', 'user_data', 'created_by', 'created_at']

    def get_user_data(self, obj):
        if obj.relation.source_partner and hasattr(obj.relation.source_partner, 'person'):
            person = obj.relation.source_partner.person
            if hasattr(person, 'user'):
                return UserWithPersonSerializer(person.user).data
        return None

    def create(self, validated_data):
        work_item_id = validated_data.pop('work_item')
        user_id = validated_data.pop('user')
        
        # Get tenant and created_by from the context (passed by the view)
        tenant = self.context.get('tenant')
        created_by = self.context.get('created_by')
        
        if not tenant or not created_by:
            raise serializers.ValidationError('Tenant and created_by must be provided.')
        
        # Get the work item and user
        from engagements.models import WorkItem
        from users.models import User
        
        try:
            work_item = WorkItem.objects.get(id=work_item_id)
        except WorkItem.DoesNotExist:
            raise serializers.ValidationError(f"Work item with ID {work_item_id} does not exist.")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with ID {user_id} does not exist.")
        
        # Validate tenant consistency
        if work_item.tenant != tenant or user.tenant != tenant:
            raise serializers.ValidationError('Work item and user must belong to your tenant.')
        
        # Get the person associated with this user through the partner relationship
        try:
            person = user.partner.person
        except (AttributeError, ObjectDoesNotExist):
            raise serializers.ValidationError(f"User {user.id} does not have an associated Person record.")
        
        # Get or create the relation using the utility function
        relation = create_or_get_assignment_relation(person, work_item, tenant, created_by)
        
        # Check if assignment already exists for this relation
        if Assignment.objects.filter(relation=relation).exists():
            raise serializers.ValidationError('User is already assigned to this work item.')
        
        # Create the assignment
        validated_data['relation'] = relation
        validated_data['tenant'] = tenant
        validated_data['created_by'] = created_by
        return super().create(validated_data) 