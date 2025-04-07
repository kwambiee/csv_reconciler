from django.core.management.base import BaseCommand
from reconciliation.services import CSVReconciler
import argparse

class Command(BaseCommand):
    help = 'Reconcile two CSV files and produce a report'
    
    def add_arguments(self, parser):
        parser.add_argument('-s', '--source', type=str, help='Path to source CSV file', required=True)
        parser.add_argument('-t', '--target', type=str, help='Path to target CSV file', required=True)
        parser.add_argument('-o', '--output', type=str, help='Path to output report file', required=True)
        parser.add_argument('--ignore', type=str, help='Comma-separated list of columns to ignore', default='')
    
    def handle(self, *args, **options):
        source_path = options['source']
        target_path = options['target']
        output_path = options['output']
        ignore_columns = [col.strip() for col in options['ignore'].split(',') if col.strip()]
        
        try:
            reconciler = CSVReconciler(
                source_path=source_path,
                target_path=target_path,
                output_path=output_path,
                ignore_columns=ignore_columns
            )
            result = reconciler.reconcile()
            
            self.stdout.write(self.style.SUCCESS(
                f"Reconciliation completed:\n"
                f"- Records missing in target: {result['missing_in_target']}\n"
                f"- Records missing in source: {result['missing_in_source']}\n"
                f"- Records with field discrepancies: {result['field_discrepancies']}\n\n"
                f"Report saved to: {output_path}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))