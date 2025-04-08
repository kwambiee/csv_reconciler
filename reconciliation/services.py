import pandas as pd
from datetime import timezone, datetime
from dateutil.parser import parse

class CSVReconciler:
    def __init__(self, source_path, target_path, output_path=None, ignore_columns=None):
        self.source_path = source_path
        self.target_path = target_path
        self.output_path = output_path
        self.ignore_columns = ignore_columns or []
        
    def read_csv(self, file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Error reading {file_path}: {str(e)}")
    
    def normalize_data(self, df):
        # Convert all strings to lowercase and strip whitespace
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        
        # Try to parse dates
        for col in df.columns:
            if 'date' in col.lower():
                df[col] = df[col].apply(self.try_parse_date)
        return df
    
    
    def try_parse_date(self, value):
        if pd.isna(value):
            return pd.NaT  # Ensure it's consistent with pandas expectations
        try:
            dt = parse(value)
            if isinstance(dt, datetime) and dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc)
            return dt
        except (ValueError, TypeError):
            return pd.NaT
    
    
    def reconcile(self):
        source_df = self.read_csv(self.source_path)
        target_df = self.read_csv(self.target_path)
        
        # Normalize data
        source_df = self.normalize_data(source_df)
        target_df = self.normalize_data(target_df)
        
        
        # Get ID column name (assume first column)
        id_col = source_df.columns[0]
        
        # Filter out ignored columns
        compare_cols = [col for col in source_df.columns 
                       if col not in self.ignore_columns and col in target_df.columns]
        
        # Find missing records
        source_ids = set(source_df[id_col])
        target_ids = set(target_df[id_col])
        
        missing_in_target = source_df[~source_df[id_col].isin(target_ids)]
        missing_in_source = target_df[~target_df[id_col].isin(source_ids)]
        
        
        # Find common records
        common_ids = source_ids & target_ids
        common_source = source_df[source_df[id_col].isin(common_ids)]
        common_target = target_df[target_df[id_col].isin(common_ids)]
        
        # Find discrepancies
        discrepancies = []
        for _, s_row in common_source.iterrows():
            t_row = common_target[common_target[id_col] == s_row[id_col]].iloc[0]
            for col in compare_cols:
                if col == id_col:
                    continue
                s_val = s_row[col]
                t_val = t_row[col]
                
                if s_val != t_val:
                    discrepancies.append({
                        'type': 'field_discrepancy',
                        'id': s_row[id_col],
                        'field': col,
                        'source_value': s_val,
                        'target_value': t_val
                    })
        
        # Prepare results
        results = []
        
        
        # Add missing records
        for _, row in missing_in_target.iterrows():
            results.append({
                'type': 'missing_in_target',
                'id': row[id_col],
                'field': None,
                'source_value': None,
                'target_value': None
            })
            
        for _, row in missing_in_source.iterrows():
            results.append({
                'type': 'missing_in_source',
                'id': row[id_col],
                'field': None,
                'source_value': None,
                'target_value': None
            })
            
        # Add discrepancies
        results.extend(discrepancies)
        
        # Convert to DataFrame
        result_df = pd.DataFrame(results, columns=[
            'type', 'id', 'field', 'source_value', 'target_value'
        ])
        from datetime import datetime

        result_df['source_value'] = result_df['source_value'].apply(
            lambda x: x.isoformat() if isinstance(x, datetime) else ("" if pd.isna(x) else x)
        )

        result_df['target_value'] = result_df['target_value'].apply(
            lambda x: x.isoformat() if isinstance(x, datetime) else ("" if pd.isna(x) else x)
        )

        
        # Save if output path provided
        if self.output_path:           
            result_df.to_csv(self.output_path, index=False)
            
            
        return {
            'missing_in_target': len(missing_in_target),
            'missing_in_source': len(missing_in_source),
            'field_discrepancies': len(discrepancies),
            'results': result_df.to_dict('records')
        }
        
        
    def calculate_differences(self, s_val, t_val):
        """Calculate numerical differences between values if possible"""
        try:
            s_num = float(s_val)
            t_num = float(t_val)
            return abs(s_num - t_num)
        except (ValueError, TypeError):
            return None

    def reconcile(self):
        source_df = self.read_csv(self.source_path)
        target_df = self.read_csv(self.target_path)
        
        # Normalize data
        source_df = self.normalize_data(source_df)
        target_df = self.normalize_data(target_df)
        
        # Get ID column name (assume first column)
        id_col = source_df.columns[0]
        
        # Filter out ignored columns
        compare_cols = [col for col in source_df.columns 
                    if col not in self.ignore_columns and col in target_df.columns]
        
        # Find missing records
        source_ids = set(source_df[id_col])
        target_ids = set(target_df[id_col])
        
        missing_in_target = source_df[~source_df[id_col].isin(target_ids)]
        missing_in_source = target_df[~target_df[id_col].isin(source_ids)]
        
        # Find common records
        common_ids = source_ids & target_ids
        common_source = source_df[source_df[id_col].isin(common_ids)]
        common_target = target_df[target_df[id_col].isin(common_ids)]
        
        # Find discrepancies
        discrepancies = []
        for _, s_row in common_source.iterrows():
            t_row = common_target[common_target[id_col] == s_row[id_col]].iloc[0]
            for col in compare_cols:
                if col == id_col:
                    continue
                s_val = s_row[col]
                t_val = t_row[col]
                
                if pd.isna(s_val) and pd.isna(t_val):
                    continue
                    
                if s_val != t_val:
                    difference = self.calculate_differences(s_val, t_val)
                    discrepancy_type = self.get_discrepancy_type(s_val, t_val)
                    
                    discrepancies.append({
                        'type': 'field_discrepancy',
                        'id': s_row[id_col],
                        'field': col,
                        'source_value': s_val,
                        'target_value': t_val,
                        'discrepancy_type': discrepancy_type,
                        'difference': difference
                    })
        
        # Prepare results
        results = []
    
        # Add missing records
        # for _, row in missing_in_target.iterrows():
        #     results.append({
        #         'type': 'missing_in_target',
        #         'id': row[id_col],
        #         'field': None,
        #         'source_value': None,
        #         'target_value': None,
        #         'discrepancy_type': None,
        #         'difference': None
        #     })
            
        # for _, row in missing_in_source.iterrows():
        #     results.append({
        #         'type': 'missing_in_source',
        #         'id': row[id_col],
        #         'field': None,
        #         'source_value': None,
        #         'target_value': None,
        #         'discrepancy_type': None,
        #         'difference': None
        #     })
        
        
        # In service.py, modify the missing records sections:

    # Add missing records
        for _, row in missing_in_target.iterrows():
            results.append({
                'type': 'missing_in_target',
                'id': row[id_col],
                'field': 'complete_record',
                'source_value': row.to_dict(),
                'target_value': None,
                'discrepancy_type': 'missing_record',
                'difference': None
            })
    
        for _, row in missing_in_source.iterrows():
            results.append({
                'type': 'missing_in_source',
                'id': row[id_col],
                'field': 'complete_record',
                'source_value': None,
                'target_value': row.to_dict(),
                'discrepancy_type': 'missing_record',
                'difference': None
            })
        # Add discrepancies
        results.extend(discrepancies)
        
        # Convert to DataFrame
        result_df = pd.DataFrame(results, columns=[
            'type', 'id', 'field', 'source_value', 'target_value',
            'discrepancy_type', 'difference'
        ])
        
        # Format datetime values
        for col in ['source_value', 'target_value']:
            result_df[col] = result_df[col].apply(
                lambda x: x.isoformat() if isinstance(x, (pd.Timestamp, datetime)) else x
            )
        
        # Save if output path provided
        if self.output_path:           
            result_df.to_csv(self.output_path, index=False)
            
        return {
            'missing_in_target': len(missing_in_target),
            'missing_in_source': len(missing_in_source),
            'field_discrepancies': len(discrepancies),
            'results': result_df.to_dict('records')
    }

    def get_discrepancy_type(self, s_val, t_val):
        """Determine the type of discrepancy"""
        if pd.isna(s_val) and not pd.isna(t_val):
            return "Missing in source"
        elif not pd.isna(s_val) and pd.isna(t_val):
            return "Missing in target"
        elif isinstance(s_val, (int, float)) and isinstance(t_val, (int, float)):
            return "Numerical difference"
        else:
            return "Value mismatch"