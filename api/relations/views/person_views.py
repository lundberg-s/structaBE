from relations.models import Person  

from relations.serializers.person_serializers import PersonSerializer

from relations.views.partner_views import PartnerListView, PartnerDetailView

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