import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csv_reconciler.settings')
django.setup()