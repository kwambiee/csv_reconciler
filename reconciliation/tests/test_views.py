from django.test import TestCase, Client
from django.urls import reverse
import tempfile

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CSV Reconciliation Tool")
        
    def test_upload_view_get(self):
        response = self.client.get(reverse('upload'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload CSV Files")
        
    def test_upload_view_post(self):
        # Create test files
        source_file = tempfile.NamedTemporaryFile(suffix='.csv')
        target_file = tempfile.NamedTemporaryFile(suffix='.csv')
        
        source_file.write(b'ID,Name\n001,John Doe\n002,Jane Smith')
        target_file.write(b'ID,Name\n001,John Doe\n003,Robert Brown')
        
        source_file.seek(0)
        target_file.seek(0)
        
        response = self.client.post(reverse('upload'), {
            'source': source_file,
            'target': target_file
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reconciliation Report")
        
        source_file.close()
        target_file.close()