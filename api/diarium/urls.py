from django.urls import path, include
from rest_framework.routers import DefaultRouter
from diarium.views.workitem_views import CurrentWorkItemListView, CurrentWorkItemDetailView
from diarium.views.entity_views import CustomerViewSet, OrganizationViewSet, VendorViewSet
from diarium.views.workitem_entity_role_views import WorkItemEntityRoleViewSet
from diarium.views.attachments_views import AttachmentListCreateView, AttachmentRetrieveUpdateDestroyView
from diarium.views.comments_views import CommentListCreateView, CommentRetrieveUpdateDestroyView
from diarium.views.activity_logs_views import ActivityLogListCreateView, ActivityLogRetrieveView
from diarium.views.statistics_views import WorkItemStatisticsView

app_name = 'diarium'

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'vendors', VendorViewSet, basename='vendor')
router.register(r'workitem-entity-roles', WorkItemEntityRoleViewSet, basename='workitementityrole')

urlpatterns = [
    path('', include(router.urls)),
    path('attachments/', AttachmentListCreateView.as_view(), name='attachment-list-create'),
    path('attachments/<uuid:id>/', AttachmentRetrieveUpdateDestroyView.as_view(), name='attachment-detail'),
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<uuid:id>/', CommentRetrieveUpdateDestroyView.as_view(), name='comment-detail'),
    path('activity-logs/', ActivityLogListCreateView.as_view(), name='activity-log-list-create'),
    path('activity-logs/<uuid:id>/', ActivityLogRetrieveView.as_view(), name='activity-log-detail'),
    path('statistics/', WorkItemStatisticsView.as_view(), name='workitem-statistics'),
    path('workitems/', CurrentWorkItemListView.as_view(), name='current-workitem-list'),
    path('workitems/<uuid:pk>/', CurrentWorkItemDetailView.as_view(), name='current-workitem-detail'),
]
