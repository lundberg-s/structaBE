from django.urls import path
from user.views import UserMeView, UserListView

app_name = "core"

urlpatterns = [
    path("me/", UserMeView.as_view(), name="user-me"),
    path("list/", UserListView.as_view(), name="user-list-view"),
]
