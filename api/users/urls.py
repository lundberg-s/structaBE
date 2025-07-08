from django.urls import path

from users.views.signup_views import SignupView
from users.views.user_views import UserMeView, UserListView, UserDetailView
from relations.views.person_views import PersonListView, PersonDetailView
from relations.views.organization_views import OrganizationListView, OrganizationDetailView

app_name = "core"

urlpatterns = [
    path("me/", UserMeView.as_view(), name="user-me"),
    path("sign-up/", SignupView.as_view(), name="sign-up"),

    path("users/", UserListView.as_view(), name="user-list-view"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),

    path("persons/", PersonListView.as_view(), name="person-list"),
    path("persons/<uuid:pk>/", PersonDetailView.as_view(), name="person-detail"),

    path("organizations/", OrganizationListView.as_view(), name="organization-list"),
    path("organizations/<uuid:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
]
