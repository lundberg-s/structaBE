from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from rest_framework import serializers
from rest_framework.response import Response

from relations.models import Assignment
from relations.serializers.assignment_serializers import AssignmentSerializer, AssignmentCreateSerializer
from core.views.base_views import BaseView


class AssignmentCreateView(BaseView, CreateAPIView):
    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssignmentCreateSerializer
        return AssignmentSerializer

    def get_serializer_context(self):
        """Add tenant and created_by to serializer context."""
        context = super().get_serializer_context()
        context['tenant'] = self.get_tenant()
        context['created_by'] = self.get_user()
        return context

    def perform_create(self, serializer):
        """Create the assignment and log the activity."""
        instance = serializer.save()
        self.log_activity(instance, 'assigned', 'assigned')