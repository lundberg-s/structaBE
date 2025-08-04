from rest_framework.generics import RetrieveUpdateDestroyAPIView
from partners.models import Person  

from partners.serializers import PersonSerializer

from partners.views import PartnerListView, PartnerDetailView

class PersonListView(PartnerListView):
    model = Person
    serializer_class = PersonSerializer
    
    def get_queryset(self):
        return Person.objects.filter(tenant=self.request.user.tenant)

class PersonDetailView(PartnerDetailView):
    model = Person
    serializer_class = PersonSerializer
    
    def get_queryset(self):
        return Person.objects.filter(tenant=self.request.user.tenant)