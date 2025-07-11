from django.urls import path
from engagements.views.work_item_views import TicketListView, CaseListView, JobListView, TicketDetailView, CaseDetailView, JobDetailView
from engagements.views.assignment_views import AssignmentCreateView
from engagements.views.work_item_partner_role_views import WorkItemPartnerRoleListView, WorkItemPartnerRoleDetailView
from engagements.views.attachments_views import AttachmentListView, AttachmentDetailView
from engagements.views.comments_views import CommentListView, CommentDetailView
from engagements.views.activity_logs_views import ActivityLogListView, ActivityLogDetailView
from engagements.views.statistics_views import WorkItemStatisticsView

app_name = 'engagements'


urlpatterns = [
    path('work_item-partner-roles/', WorkItemPartnerRoleListView.as_view(), name='work_item-partner-role-list'),
    path('work_item-partner-roles/<uuid:pk>/', WorkItemPartnerRoleDetailView.as_view(), name='work_item-partner-role-detail'),

    path('tickets/', TicketListView.as_view(), name='ticket-list'),
    path('tickets/<uuid:pk>/', TicketDetailView.as_view(), name='ticket-detail'),

    path('cases/', CaseListView.as_view(), name='case-list'),
    path('cases/<uuid:pk>/', CaseDetailView.as_view(), name='case-detail'),

    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<uuid:pk>/', JobDetailView.as_view(), name='job-detail'),

    path('attachments/', AttachmentListView.as_view(), name='attachment-list'),
    path('attachments/<uuid:id>/', AttachmentDetailView.as_view(), name='attachment-detail'),

    path('comments/', CommentListView.as_view(), name='comment-list'),
    path('comments/<uuid:id>/', CommentDetailView.as_view(), name='comment-detail'),

    path('activity-logs/', ActivityLogListView.as_view(), name='activity-log-list'),
    path('activity-logs/<uuid:id>/', ActivityLogDetailView.as_view(), name='activity-log-detail'),
    
    path('statistics/', WorkItemStatisticsView.as_view(), name='work_item-statistics'),
    path('assignments/', AssignmentCreateView.as_view(), name='assignment-create'),
]
