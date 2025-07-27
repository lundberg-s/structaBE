from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from rest_framework import serializers
from rest_framework.response import Response

from engagements.models import Assignment
from engagements.serializers.assignment_serializers import AssignmentSerializer, AssignmentCreateSerializer
from core.views.base_views import BaseView


class AssignmentCreateView(BaseView, CreateAPIView):
    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssignmentCreateSerializer
        return AssignmentSerializer

    def perform_create(self, serializer):
        # Tenant scoping validation
        work_item = serializer.validated_data['work_item']
        user = serializer.validated_data['user']
        request_tenant = self.get_tenant()
        if work_item.tenant != request_tenant or user.tenant != request_tenant:
            raise serializers.ValidationError('Work item and user must belong to your tenant.')
        
        # Save with tenant and created_by
        instance = serializer.save(
            tenant=request_tenant,
            created_by=self.get_user()
        )
        
        self.log_activity(instance, 'assigned', 'assigned')