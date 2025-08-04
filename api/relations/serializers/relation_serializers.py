from rest_framework import serializers

from relations.models import Relation
from partners.models import Partner, Person
from relations.choices import RelationObjectType
from engagements.models import WorkItem


class RelationSerializer(serializers.ModelSerializer):
    source_partner_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    source_workitem_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    target_partner_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    target_workitem_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    role_id = serializers.UUIDField(write_only=True)
    source_type = serializers.CharField(read_only=True)
    target_type = serializers.CharField(read_only=True)

    class Meta:
        model = Relation
        fields = [
            'id', 'source_partner_id', 'source_workitem_id', 'target_partner_id', 'target_workitem_id',
            'source_type', 'target_type', 'role_id', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """
        Validate Relation data:
        1. Exactly one source reference (partner OR workitem) must be set
        2. Exactly one target reference (partner OR workitem) must be set
        3. Source and target cannot be the same
        4. Tenant consistency
        """
        source_partner_id = data.get('source_partner_id')
        source_workitem_id = data.get('source_workitem_id')
        target_partner_id = data.get('target_partner_id')
        target_workitem_id = data.get('target_workitem_id')
        
        # 1. Validate exactly one source reference
        if bool(source_partner_id) == bool(source_workitem_id):
            raise serializers.ValidationError(
                "Exactly one source reference must be set: either source_partner_id OR source_workitem_id"
            )
        
        # 2. Validate exactly one target reference
        if bool(target_partner_id) == bool(target_workitem_id):
            raise serializers.ValidationError(
                "Exactly one target reference must be set: either target_partner_id OR target_workitem_id"
            )
        
        # 3. Validate source and target are different
        if source_partner_id and target_partner_id and source_partner_id == target_partner_id:
            raise serializers.ValidationError("Source and target cannot be the same.")
        
        if source_workitem_id and target_workitem_id and source_workitem_id == target_workitem_id:
            raise serializers.ValidationError("Source and target cannot be the same.")
        
        # 4. Validate tenant consistency
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            tenant = request.user.tenant
            
            # Check source tenant
            if source_partner_id:
                try:
                    source_partner = Partner.objects.get(id=source_partner_id)
                    if source_partner.tenant != tenant:
                        raise serializers.ValidationError("Source partner must belong to the same tenant")
                except Partner.DoesNotExist:
                    raise serializers.ValidationError("Invalid source partner reference")
            
            if source_workitem_id:
                try:
                    source_workitem = WorkItem.objects.get(id=source_workitem_id)
                    if source_workitem.tenant != tenant:
                        raise serializers.ValidationError("Source workitem must belong to the same tenant")
                except WorkItem.DoesNotExist:
                    raise serializers.ValidationError("Invalid source workitem reference")
            
            # Check target tenant
            if target_partner_id:
                try:
                    target_partner = Partner.objects.get(id=target_partner_id)
                    if target_partner.tenant != tenant:
                        raise serializers.ValidationError("Target partner must belong to the same tenant")
                except Partner.DoesNotExist:
                    raise serializers.ValidationError("Invalid target partner reference")
            
            if target_workitem_id:
                try:
                    target_workitem = WorkItem.objects.get(id=target_workitem_id)
                    if target_workitem.tenant != tenant:
                        raise serializers.ValidationError("Target workitem must belong to the same tenant")
                except WorkItem.DoesNotExist:
                    raise serializers.ValidationError("Invalid target workitem reference")
        
        return data

    def create(self, validated_data):
        source_partner_id = validated_data.pop('source_partner_id', None)
        source_workitem_id = validated_data.pop('source_workitem_id', None)
        target_partner_id = validated_data.pop('target_partner_id', None)
        target_workitem_id = validated_data.pop('target_workitem_id', None)
        role_id = validated_data.pop('role_id')
        
        # Set source fields
        if source_partner_id:
            validated_data['source_partner_id'] = source_partner_id
            source_partner = Partner.objects.get(id=source_partner_id)
            validated_data['source_type'] = RelationObjectType.PERSON if isinstance(source_partner, Person) else RelationObjectType.ORGANIZATION
        else:
            validated_data['source_workitem_id'] = source_workitem_id
            validated_data['source_type'] = RelationObjectType.WORKITEM
        
        # Set target fields
        if target_partner_id:
            validated_data['target_partner_id'] = target_partner_id
            target_partner = Partner.objects.get(id=target_partner_id)
            validated_data['target_type'] = RelationObjectType.PERSON if isinstance(target_partner, Person) else RelationObjectType.ORGANIZATION
        else:
            validated_data['target_workitem_id'] = target_workitem_id
            validated_data['target_type'] = RelationObjectType.WORKITEM
        
        # Set role
        from core.models import Role
        validated_data['role'] = Role.objects.get(id=role_id)
        
        # Set tenant
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['tenant'] = request.user.tenant
        
        return Relation.objects.create(**validated_data) 