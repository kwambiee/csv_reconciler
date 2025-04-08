from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .services import CSVReconciler
from django.views import View
from django.http import JsonResponse, HttpResponse
from .models import UploadedFile, ReconciliationReport
import pandas as pd
import os
import uuid
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.text import slugify
import json
import ast

class CSVReconciliationAPI(APIView):
    def post(self, request):
        source_file = request.FILES.get('source')
        target_file = request.FILES.get('target')
        
        if not source_file or not target_file:
            return Response(
                {'error': 'Both source and target files are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Save files to persistent storage
            source_upload = self.save_uploaded_file(source_file, 'source')
            target_upload = self.save_uploaded_file(target_file, 'target')
            
            # Get ignore columns from request
            ignore_columns = request.data.get('ignore_columns', '').split(',')
            ignore_columns = [col.strip() for col in ignore_columns if col.strip()]
            
            # Perform reconciliation
            reconciler = CSVReconciler(
                source_path=source_upload.file.path,
                target_path=target_upload.file.path,
                ignore_columns=ignore_columns
            )
            result = reconciler.reconcile()
            
            # Save report
            report = self.save_report(source_upload, target_upload, ignore_columns, result)
            
            return Response({
                'report_id': report.id,
                'results': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def save_uploaded_file(self, file, file_type):
        original_filename = file.name
        file_upload = UploadedFile(
            file=file,
            original_filename=original_filename,
            file_type=file_type
        )
        
        # Read the file to get metadata
        try:
            df = pd.read_csv(file)
            file_upload.row_count = len(df)
            file_upload.columns = list(df.columns)
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
        
        file_upload.save()
        return file_upload
    
    def save_report(self, source_upload, target_upload, ignore_columns, result):
        # Generate report filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"report_{source_upload.id}_{target_upload.id}_{timestamp}.csv"
        
        # Save results to CSV
        results_df = pd.DataFrame(result['results'])
        report_content = results_df.to_csv(index=False)
        
        # Create report file
        report_file = ContentFile(report_content.encode('utf-8'), name=report_filename)
        
        # Create report record
        report = ReconciliationReport(
            source_file=source_upload,
            target_file=target_upload,
            missing_in_target=result['missing_in_target'],
            missing_in_source=result['missing_in_source'],
            field_discrepancies=result['field_discrepancies'],
            ignore_columns=ignore_columns
        )
        report.report_file.save(report_filename, report_file)
        report.save()
        
        return report

class HomeView(View):
    def get(self, request):
        # Show recent reports
        recent_reports = ReconciliationReport.objects.all().order_by('-created_at')[:5]
        return render(request, 'reconciliation/home.html', {
            'recent_reports': recent_reports
        })

class UploadView(View):
    def get(self, request):
        return render(request, 'reconciliation/upload.html')
    
    def post(self, request):
        source_file = request.FILES.get('source')
        target_file = request.FILES.get('target')
        ignore_columns = request.POST.get('ignore_columns', '')
        
        if not source_file or not target_file:
            return render(request, 'reconciliation/upload.html', {
                'error': 'Both source and target files are required'
            })
        
        try:
            # Save files to persistent storage
            source_upload = self.save_uploaded_file(source_file, 'source')
            target_upload = self.save_uploaded_file(target_file, 'target')
            
            # Process ignore columns
            ignore_list = [col.strip() for col in ignore_columns.split(',') if col.strip()]
            
            # Perform reconciliation
            reconciler = CSVReconciler(
                source_path=source_upload.file.path,
                target_path=target_upload.file.path,
                ignore_columns=ignore_list
            )
            result = reconciler.reconcile()
            
            # Save report
            report = self.save_report(source_upload, target_upload, ignore_list, result)
            
            return redirect('report_detail', report_id=report.id)
            
        except Exception as e:
            return render(request, 'reconciliation/upload.html', {
                'error': str(e)
            })
    
    def save_uploaded_file(self, file, file_type):
        original_filename = file.name
        file_upload = UploadedFile(
            file=file,
            original_filename=original_filename,
            file_type=file_type
        )
        
        # Read the file to get metadata
        try:
            df = pd.read_csv(file)
            file_upload.row_count = len(df)
            file_upload.columns = list(df.columns)
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
        
        file_upload.save()
        return file_upload
    
    # def save_report(self, source_upload, target_upload, ignore_columns, result):
    #     # Generate report filename
    #     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    #     report_filename = f"report_{source_upload.id}_{target_upload.id}_{timestamp}.csv"
        
    #     # Save results to CSV
    #     results_df = pd.DataFrame(result['results'])
    #     report_content = results_df.to_csv(index=False)
        
    #     # Create report file
    #     report_file = ContentFile(report_content.encode('utf-8'), name=report_filename)
        
    #     print(results_df, "----results_df")
        
    #     # Create report record
    #     report = ReconciliationReport(
    #         source_file=source_upload,
    #         target_file=target_upload,
    #         missing_in_target=result['missing_in_target'],
    #         missing_in_source=result['missing_in_source'],
    #         field_discrepancies=result['field_discrepancies'],
    #         ignore_columns=ignore_columns,
    #     )
    #     report.report_file.save(report_filename, report_file)
    #     report.save()
        
    #     return report
    
    
    def save_report(self, source_upload, target_upload, ignore_columns, result):
        # Generate report filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"report_{source_upload.id}_{target_upload.id}_{timestamp}.csv"
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(result['results'])
        
        # Handle dictionary values in source_value and target_value
        for col in ['source_value', 'target_value']:
            if results_df[col].apply(lambda x: isinstance(x, dict)).any():
                print (results_df[col], "----results_df[col]")
                results_df[col] = results_df[col].apply(
                    lambda x: str(x) if isinstance(x, dict) else x
                )
        
        # Save results to CSV
        report_content = results_df.to_csv(index=False)
        
        # Create report file
        report_file = ContentFile(report_content.encode('utf-8'), name=report_filename)
        
        # Create report record
        report = ReconciliationReport(
            source_file=source_upload,
            target_file=target_upload,
            missing_in_target=result['missing_in_target'],
            missing_in_source=result['missing_in_source'],
            field_discrepancies=result['field_discrepancies'],
            ignore_columns=ignore_columns,
        )
        report.report_file.save(report_filename, report_file)
        report.save()
        
        return report

class ReportDetailView(View):    
    def get(self, request, report_id):
        report = get_object_or_404(ReconciliationReport, id=report_id)
        
        # Get filter parameters
        discrepancy_type = request.GET.get('type', '')
        # field_name = request.GET.get('field', '')
        search_query = request.GET.get('search', '')
        
        # Read report data
        results_df = pd.read_csv(report.report_file.path)
        
        # Convert JSON strings back to dictionaries
        for col in ['source_value', 'target_value']:
            if results_df[col].apply(lambda x: isinstance(x, str) and x.startswith('{') and x.endswith('}')).any():
                for idx, val in results_df[col].items():
                    try:
                        if isinstance(val, str) and val.startswith('{') and val.endswith('}'):
                            val = val.replace("'", '"')
                            results_df.at[idx, col] = json.loads(val)
                    except json.JSONDecodeError as e:
                        print(f"JSON Decode Error: {e} at index {idx} in column {col}")
                        print(f"Value: {val}")

        results = results_df.to_dict('records')
        
        # Apply filters
        filtered_results = results
        if discrepancy_type:
            filtered_results = [r for r in filtered_results if r['type'] == discrepancy_type]
        if search_query:
            search_query = search_query.lower()
            filtered_results = [
                r for r in filtered_results 
                if search_query in str(r['id']).lower() or 
                    (r['field'] and search_query in str(r['field']).lower()) or
                    (r['source_value'] and search_query in str(r['source_value']).lower()) or
                    (r['target_value'] and search_query in str(r['target_value']).lower())
            ]
        
        # Pagination
        paginator = Paginator(filtered_results, 50)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Get unique values for filters
        unique_types = results_df['type'].unique()
        unique_fields = results_df['field'].dropna().unique()
        
        # Prepare modal results
        model_results = []
        for result in filtered_results:
            if result.get('field') == "complete_record":
                val = result.get('source_value') or result.get('target_value')
                if isinstance(val, dict):
                    val = [val]
                    
                model_results.append({
                    'id': result.get('id'),
                    'field': result.get('field'),
                    'source_value': val,
                    'target_value': val,
                })

        # Always return a response
        return render(request, 'reconciliation/report_detail.html', {
            'report': report,
            'results': page_obj,  # Use paginated results
            'unique_types': unique_types,
            'unique_fields': unique_fields,
            'current_type_filter': discrepancy_type,
            'search_query': search_query,
            'modal_results': model_results,
        })

class FilePreviewView(View):
    def get(self, request, file_id):
        file = get_object_or_404(UploadedFile, id=file_id)
        
        # Read sample data (first 50 rows)
        try:
            df = pd.read_csv(file.file.path)
            sample_data = df.head(50).to_dict('records')
            columns = df.columns.tolist()
        except Exception as e:
            return render(request, 'reconciliation/error.html', {
                'error': f"Could not read file: {str(e)}"
            })
        
        return render(request, 'reconciliation/file_preview.html', {
            'file': file,
            'sample_data': sample_data,
            'columns': columns,
            'row_count': len(df)
        })

class ReportHistoryView(View):
    def get(self, request):
        search_query = request.GET.get('q', '')
        
        reports = ReconciliationReport.objects.all().order_by('-created_at')
        
        if search_query:
            reports = reports.filter(
                Q(source_file__original_filename__icontains=search_query) |
                Q(target_file__original_filename__icontains=search_query)
            )
        
        paginator = Paginator(reports, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'reconciliation/report_history.html', {
            'reports': page_obj,
            'search_query': search_query
        })