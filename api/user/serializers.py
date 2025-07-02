from rest_framework import serializers

from user.models import User, Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["name", "workitem_type"]


class UserSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "tenant"]
