from django.urls import path, include
from rest_framework.routers import DefaultRouter
from engagements.views.work_item_views import TicketWorkItemListView, CaseWorkItemListView, JobWorkItemListView, TicketWorkItemDetailView, CaseWorkItemDetailView, JobWorkItemDetailView
from engagements.views.assignment_views import AssignmentCreateView
from engagements.views.work_item_partner_role_views import WorkItemPartnerRoleListView, WorkItemPartnerRoleDetailView
from engagements.views.attachments_views import AttachmentListCreateView, AttachmentRetrieveUpdateDestroyView
from engagements.views.comments_views import CommentListCreateView, CommentRetrieveUpdateDestroyView
from engagements.views.activity_logs_views import ActivityLogListCreateView, ActivityLogRetrieveView
from engagements.views.statistics_views import WorkItemStatisticsView

app_name = 'engagements'


urlpatterns = [
    path('work_item-partner-roles/', WorkItemPartnerRoleListView.as_view(), name='work_item-partner-role-list'),
    path('work_item-partner-roles/<uuid:pk>/', WorkItemPartnerRoleDetailView.as_view(), name='work_item-partner-role-detail'),

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
    
    path('statistics/', WorkItemStatisticsView.as_view(), name='work_item-statistics'),
    path('assignments/', AssignmentCreateView.as_view(), name='assignment-create'),
]
