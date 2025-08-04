from rest_framework.serializers import ModelSerializer, SerializerMethodField

from partners.models import Partner

class PartnerSerializer(ModelSerializer):
    content_type = SerializerMethodField()

    class Meta:
        model = Partner
        fields = ['id', 'content_type']
        read_only_fields = ['id', 'content_type']

    def get_content_type(self, obj):
        return obj._meta.model_name