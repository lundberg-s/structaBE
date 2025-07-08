from user.models import Person  

from user.serializers.person_serializers import PersonSerializer

from user.views.partner_views import PartnerListView, PartnerDetailView

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