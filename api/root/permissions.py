from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import GenericAPIView

class ConditionalPermissionView(GenericAPIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]