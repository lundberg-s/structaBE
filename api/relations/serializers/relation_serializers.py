from rest_framework import serializers
from django.core.exceptions import ValidationError
from relations.models import Relation, RelationReference


class RelationReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationReference
        fields = ['id', 'type', 'partner', 'workitem']


class RelationSerializer(serializers.ModelSerializer):
    source = RelationReferenceSerializer(read_only=True)
    target = RelationReferenceSerializer(read_only=True)
    source_id = serializers.UUIDField(write_only=True)
    target_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Relation
        fields = ['id', 'source', 'target', 'source_id', 'target_id', 'relation_type', 'created_at', 'updated_at']

    def validate(self, data):
        source_id = data.get('source_id')
        target_id = data.get('target_id')
        
        if source_id and target_id and source_id == target_id:
            raise ValidationError("Source and target cannot be the same.")
        
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