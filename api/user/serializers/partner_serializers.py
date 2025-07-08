from rest_framework.serializers import ModelSerializer, SerializerMethodField

from user.models import Partner

class PartnerSerializer(ModelSerializer):
    role = SerializerMethodField()
    content_type = SerializerMethodField()

    class Meta:
        model = Partner
        fields = ['id', 'role', 'content_type']

    def get_role(self, obj):
        role = obj.roles.first()
        return role.get_role_type_display() if role else None

    def get_content_type(self, obj):
        return obj._meta.model_name