from rest_framework import serializers
from django.core.exceptions import ValidationError
from relations.models import Relation, RelationReference
from relations.utilities.validation_helpers import get_real_instance
from relations.models import Person, Organization


class RelationReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationReference
        fields = ['id', 'type', 'partner', 'workitem']

    def validate(self, data):
        """
        Validate RelationReference data:
        1. Exactly one reference (partner OR workitem) must be set
        2. Type must match the actual object type
        3. Workitem type consistency
        """
        partner = data.get('partner')
        workitem = data.get('workitem')
        ref_type = data.get('type')

        # 1. Validate exactly one reference is set
        if bool(partner) == bool(workitem):
            raise serializers.ValidationError(
                "Exactly one reference must be set: either partner OR workitem"
            )

        # 2. Validate type matches FK subclass
        if partner:
            real_instance = get_real_instance(partner)
            type_mapping = {Person: "person", Organization: "organization"}
            
            if isinstance(real_instance, Person) and ref_type != "person":
                raise serializers.ValidationError(
                    f"Type must be 'person' for Person objects, got '{ref_type}'"
                )
            elif isinstance(real_instance, Organization) and ref_type != "organization":
                raise serializers.ValidationError(
                    f"Type must be 'organization' for Organization objects, got '{ref_type}'"
                )

        # 3. Validate workitem type consistency
        if workitem and ref_type != "workitem":
            raise serializers.ValidationError(
                "Type must be 'workitem' if workitem FK is set"
            )

        return data


class RelationSerializer(serializers.ModelSerializer):
    source = RelationReferenceSerializer(read_only=True)
    target = RelationReferenceSerializer(read_only=True)
    source_id = serializers.UUIDField(write_only=True)
    target_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Relation
        fields = ['id', 'source', 'target', 'source_id', 'target_id', 'relation_type', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate Relation data:
        1. Source and target cannot be the same
        2. Tenant consistency between source and target
        """
        source_id = data.get('source_id')
        target_id = data.get('target_id')
        
        # 1. Validate source and target are different
        if source_id and target_id and source_id == target_id:
            raise serializers.ValidationError("Source and target cannot be the same.")
        
        # 2. Validate tenant consistency
        if source_id and target_id:
            try:
                source = RelationReference.objects.get(id=source_id)
                target = RelationReference.objects.get(id=target_id)
                
                # Get the actual objects to check tenant
                source_obj = RelationReference.objects.get_object(source)
                target_obj = RelationReference.objects.get_object(target)
                
                if source_obj and target_obj:
                    # Check if both objects have tenant and they match
                    if hasattr(source_obj, 'tenant') and hasattr(target_obj, 'tenant'):
                        if source_obj.tenant != target_obj.tenant:
                            raise serializers.ValidationError(
                                "Source and target must belong to the same tenant"
                            )
            except RelationReference.DoesNotExist:
                raise serializers.ValidationError("Invalid source or target reference")
        
        return data

    def create(self, validated_data):
        source_id = validated_data.pop('source_id')
        target_id = validated_data.pop('target_id')
        
        source = RelationReference.objects.get(id=source_id)
        target = RelationReference.objects.get(id=target_id)
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['tenant'] = request.user.tenant
        
        return Relation.objects.create(
            source=source,
            target=target,
            **validated_data
        ) 