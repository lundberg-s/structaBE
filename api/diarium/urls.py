from django.urls import path
from diarium.views.case_views import CaseListView, CaseDetailView
from diarium.views.attachments_views import AttachmentListCreateView, AttachmentRetrieveUpdateDestroyView
from diarium.views.comments_views import CommentListCreateView, CommentRetrieveUpdateDestroyView
from diarium.views.activity_logs_views import ActivityLogListCreateView, ActivityLogRetrieveView
from diarium.views.statistics_views import CaseStatisticsView

app_name = 'diarium'

urlpatterns = [
    # Cases endpoints
    path('cases/', CaseListView.as_view(), name='case-list'),
    path('cases/<uuid:id>/', CaseDetailView.as_view(), name='case-detail'),

    # Attachments endpoints
    path('attachments/', AttachmentListCreateView.as_view(), name='attachment-list-create'),
    path('attachments/<uuid:id>/', AttachmentRetrieveUpdateDestroyView.as_view(), name='attachment-detail'),

    # Comments endpoints
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<uuid:id>/', CommentRetrieveUpdateDestroyView.as_view(), name='comment-detail'),

    # Activity Logs endpoints
    path('activity-logs/', ActivityLogListCreateView.as_view(), name='activity-log-list-create'),
    path('activity-logs/<uuid:id>/', ActivityLogRetrieveView.as_view(), name='activity-log-detail'),

    # Statistics endpoint
    path('case-statistics/', CaseStatisticsView.as_view(), name='case-statistics'),
]
