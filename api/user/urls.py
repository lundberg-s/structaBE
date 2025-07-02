from django.urls import path
from user.views import (
    UserMeView, UserListView, UserRegistrationView,
    PersonDetailView, PersonListView, CompanyUserRegistrationView
)

app_name = "core"

urlpatterns = [
    path("me/", UserMeView.as_view(), name="user-me"),
    path("list/", UserListView.as_view(), name="user-list-view"),
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("register-company/", CompanyUserRegistrationView.as_view(), name="company-user-register"),
    path("persons/", PersonListView.as_view(), name="person-list"),
    path("persons/<uuid:pk>/", PersonDetailView.as_view(), name="person-detail"),
]
