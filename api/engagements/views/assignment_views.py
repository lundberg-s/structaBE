from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from rest_framework import serializers
from rest_framework.response import Response

from engagements.models import Assignment
from engagements.serializers.assignment_serializers import AssignmentSerializer, AssignmentCreateSerializer
from engagements.models import ActivityLog


class AssignmentCreateView(CreateAPIView):
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
        request_tenant = self.request.user.tenant
        if work_item.tenant != request_tenant or user.tenant != request_tenant:
            raise serializers.ValidationError('Work item and user must belong to your tenant.')
        
        # Save with tenant and created_by
        instance = serializer.save(
            tenant=request_tenant,
            created_by=self.request.user
        )
        
        ActivityLog.objects.create(
            tenant=request_tenant,
            work_item=work_item,
            created_by=self.request.user,
            activity_type='assigned',
            description=f'User {user.username} assigned to "{work_item.title}".'
        )