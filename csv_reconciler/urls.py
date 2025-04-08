from django.contrib import admin
from django.urls import path
from reconciliation.views import (
    HomeView, UploadView, CSVReconciliationAPI, 
    ReportDetailView, FilePreviewView, ReportHistoryView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('upload/', UploadView.as_view(), name='upload'),
    path('api/reconcile/', CSVReconciliationAPI.as_view(), name='api_reconcile'),
    path('reports/<int:report_id>/', ReportDetailView.as_view(), name='report_detail'),
    path('files/<int:file_id>/preview/', FilePreviewView.as_view(), name='file_preview'),
    path('reports/', ReportHistoryView.as_view(), name='report_history'),
]