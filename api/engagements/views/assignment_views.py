from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from rest_framework import serializers
from rest_framework.response import Response

from engagements.models import Assignment
from engagements.serializers.assignment_serializers import AssignmentSerializer, AssignmentCreateSerializer


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
        serializer.save(assigned_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output_serializer = AssignmentSerializer(serializer.instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=201, headers=headers)