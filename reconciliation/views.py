from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .services import CSVReconciler
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .services import CSVReconciler
import pandas as pd
import os
import uuid

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
            # Save files temporarily
            source_path = self.save_temp_file(source_file)
            target_path = self.save_temp_file(target_file)
            
            # Get ignore columns from request
            ignore_columns = request.data.get('ignore_columns', '').split(',')
            ignore_columns = [col.strip() for col in ignore_columns if col.strip()]
            
            # Perform reconciliation
            reconciler = CSVReconciler(
                source_path=source_path,
                target_path=target_path,
                ignore_columns=ignore_columns
            )
            result = reconciler.reconcile()
            
            # Clean up temp files
            os.remove(source_path)
            os.remove(target_path)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def save_temp_file(self, file):
        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        file_name = f"{uuid.uuid4()}_{file.name}"
        file_path = os.path.join(temp_dir, file_name)
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                
        return file_path


class HomeView(View):
    def get(self, request):
        return render(request, 'reconciliation/home.html')

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
            # Save files temporarily
            source_path = self.save_temp_file(source_file)
            target_path = self.save_temp_file(target_file)
            
            # Process ignore columns
            ignore_list = [col.strip() for col in ignore_columns.split(',') if col.strip()]
            
            # Perform reconciliation
            reconciler = CSVReconciler(
                source_path=source_path,
                target_path=target_path,
                ignore_columns=ignore_list
            )
            result = reconciler.reconcile()
            
            # Convert results to DataFrame for HTML rendering
            results_df = pd.DataFrame(result['results'])
            
            # Clean up temp files
            os.remove(source_path)
            os.remove(target_path)
            
            return render(request, 'reconciliation/report.html', {
                'missing_in_target': result['missing_in_target'],
                'missing_in_source': result['missing_in_source'],
                'field_discrepancies': result['field_discrepancies'],
                'results': results_df.to_dict('records')
            })
            
        except Exception as e:
            return render(request, 'reconciliation/upload.html', {
                'error': str(e)
            })
    
    def save_temp_file(self, file):
        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        file_path = os.path.join(temp_dir, file.name)
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                
        return file_path