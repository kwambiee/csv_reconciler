import os
import pandas as pd
from django.test import TestCase
from reconciliation.services import CSVReconciler
import tempfile

class CSVReconcilerTest(TestCase):
    def setUp(self):
        # Create sample CSV files
        self.source_data = """ID,Name,Date,Amount
001,John Doe,2023-01-01,100.00
002,Jane Smith,2023-01-02,200.50
003,Robert Brown,2023-01-03,300.75"""
        
        self.target_data = """ID,Name,Date,Amount
001,John Doe,2023-01-01,100.00
002,Jane Smith,2023-01-04,200.50
004,Emily White,2023-01-05,400.90"""
        
        # Create temp files
        self.source_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        self.target_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        
        with open(self.source_file.name, 'w') as f:
            f.write(self.source_data)
            
        with open(self.target_file.name, 'w') as f:
            f.write(self.target_data)
    
    def tearDown(self):
        os.unlink(self.source_file.name)
        os.unlink(self.target_file.name)
    
    def test_reconciliation(self):
        reconciler = CSVReconciler(
            source_path=self.source_file.name,
            target_path=self.target_file.name
        )
        result = reconciler.reconcile()
        
        self.assertEqual(result['missing_in_target'], 1)
        self.assertEqual(result['missing_in_source'], 1)
        self.assertEqual(result['field_discrepancies'], 1)
        
        # Check if the missing records are correct
        missing_in_target = [r for r in result['results'] if r['type'] == 'missing_in_target']
        self.assertEqual(len(missing_in_target), 1)
        self.assertEqual(missing_in_target[0]['id'], 3)
        
        # Check if the discrepancy is correct
        discrepancies = [r for r in result['results'] if r['type'] == 'field_discrepancy']
        self.assertEqual(len(discrepancies), 1)
        self.assertEqual(discrepancies[0]['field'], 'Date')
        self.assertEqual(discrepancies[0]['source_value'], '2023-01-02T00:00:00')
        self.assertEqual(discrepancies[0]['target_value'], '2023-01-04T00:00:00')