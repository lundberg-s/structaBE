from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView

from workflow.models import Assignment
from workflow.serializers.assignment_serializers import AssignmentSerializer, AssignmentCreateSerializer


class AssignmentCreateView(CreateAPIView):
    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssignmentCreateSerializer
        return AssignmentSerializer

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)