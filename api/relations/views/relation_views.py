from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from relations.models import Relation
from relations.serializers.relation_serializers import RelationSerializer


class RelationListCreateView(generics.ListCreateAPIView):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Relation.objects.filter(tenant=self.request.user.tenant)


class RelationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Relation.objects.filter(tenant=self.request.user.tenant) 