from rest_framework import serializers

from user.models import Tenant

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id","work_item_type"]