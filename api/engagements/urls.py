from django.urls import path, include
from rest_framework.routers import DefaultRouter

from engagements.views.ticket_views import TicketListView, TicketDetailView
from engagements.views.case_views import CaseListView, CaseDetailView
from engagements.views.job_views import JobListView, JobDetailView

from engagements.views.attachments_views import AttachmentListView, AttachmentDetailView
from engagements.views.comments_views import CommentListView, CommentDetailView
from engagements.views.statistics_views import WorkItemStatisticsView
from engagements.views.audit_views import WorkItemAuditViewSet
from engagements.views import WorkItemStatusViewSet, WorkItemPriorityViewSet, WorkItemCategoryViewSet

app_name = 'engagements'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'statuses', WorkItemStatusViewSet, basename='workitem-status')
router.register(r'priorities', WorkItemPriorityViewSet, basename='workitem-priority')
router.register(r'categories', WorkItemCategoryViewSet, basename='workitem-category')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
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
    
    path('statistics/', WorkItemStatisticsView.as_view(), name='work_item-statistics'),
    
    # Audit logs for work items
    path('audit-logs/', WorkItemAuditViewSet.as_view({'get': 'list'}), name='workitem-audit-list'),
    path('audit-logs/<uuid:pk>/', WorkItemAuditViewSet.as_view({'get': 'retrieve'}), name='workitem-audit-detail'),
]
