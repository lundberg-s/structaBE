from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from diarium.statistics_utils import get_case_statistics
from diarium.serializers import CaseStatisticsSerializer

class CaseStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = get_case_statistics()
        serializer = CaseStatisticsSerializer(stats)
        return Response(serializer.data) 