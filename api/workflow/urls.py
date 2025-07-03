from django.urls import path, include
from rest_framework.routers import DefaultRouter
from workflow.views.workitem_views import TicketWorkItemListView, CaseWorkItemListView, JobWorkItemListView, TicketWorkItemDetailView, CaseWorkItemDetailView, JobWorkItemDetailView
from workflow.views.workitem_party_role_views import WorkItemPartyRoleViewSet
from workflow.views.attachments_views import AttachmentListCreateView, AttachmentRetrieveUpdateDestroyView
from workflow.views.comments_views import CommentListCreateView, CommentRetrieveUpdateDestroyView
from workflow.views.activity_logs_views import ActivityLogListCreateView, ActivityLogRetrieveView
from workflow.views.statistics_views import WorkItemStatisticsView

app_name = 'workflow'

router = DefaultRouter()
router.register(r'workitem-party-roles', WorkItemPartyRoleViewSet, basename='workitempartyrole')

urlpatterns = [
    path('', include(router.urls)),

    path('tickets/', TicketWorkItemListView.as_view(), name='ticket-list-create'),
    path('tickets/<uuid:pk>/', TicketWorkItemDetailView.as_view(), name='ticket-detail'),

    path('cases/', CaseWorkItemListView.as_view(), name='case-list-create'),
    path('cases/<uuid:pk>/', CaseWorkItemDetailView.as_view(), name='case-detail'),

    path('jobs/', JobWorkItemListView.as_view(), name='job-list-create'),
    path('jobs/<uuid:pk>/', JobWorkItemDetailView.as_view(), name='job-detail'),

    path('attachments/', AttachmentListCreateView.as_view(), name='attachment-list-create'),
    path('attachments/<uuid:id>/', AttachmentRetrieveUpdateDestroyView.as_view(), name='attachment-detail'),

    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<uuid:id>/', CommentRetrieveUpdateDestroyView.as_view(), name='comment-detail'),

    path('activity-logs/', ActivityLogListCreateView.as_view(), name='activity-log-list-create'),
    path('activity-logs/<uuid:id>/', ActivityLogRetrieveView.as_view(), name='activity-log-detail'),
    
    path('statistics/', WorkItemStatisticsView.as_view(), name='workitem-statistics'),
]
