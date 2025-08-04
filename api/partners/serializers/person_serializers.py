from rest_framework.serializers import ModelSerializer

from partners.serializers import PartnerSerializer

from partners.models import Person

class PersonSerializer(PartnerSerializer):
    class Meta(PartnerSerializer.Meta):
        model = Person
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'role',
        ]
        read_only_fields = ['id']

class FlatPersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']