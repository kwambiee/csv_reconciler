from django.db import models
from django.utils import timezone

class UploadedFile(models.Model):
    FILE_TYPES = (
        ('source', 'Source File'),
        ('target', 'Target File'),
    )
    
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    upload_date = models.DateTimeField(default=timezone.now)
    row_count = models.IntegerField(default=0)
    columns = models.JSONField(default=list)
    
    def __str__(self):
        return f"{self.get_file_type_display()}: {self.original_filename}"

class ReconciliationReport(models.Model):
    source_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='source_reports')
    target_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='target_reports')
    report_file = models.FileField(upload_to='reports/%Y/%m/%d/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    missing_in_target = models.IntegerField(default=0)
    missing_in_source = models.IntegerField(default=0)
    field_discrepancies = models.IntegerField(default=0)
    ignore_columns = models.JSONField(default=list)
    
    def __str__(self):
        return f"Report {self.id} - {self.created_at}"