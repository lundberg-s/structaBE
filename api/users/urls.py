from django.urls import path

from users.views.signup_views import SignupView
from users.views.user_views import UserMeView, UserListView, UserDetailView

app_name = "users"

urlpatterns = [
    path("me/", UserMeView.as_view(), name="user-me"),
    path("sign-up/", SignupView.as_view(), name="sign-up"),

    path("users/", UserListView.as_view(), name="user-list-view"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
]
