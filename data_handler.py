import pandas as pd
import numpy as np
import streamlit as st
import io
from typing import Optional, Dict, Any, List

class DataHandler:
    """Handles data loading, processing, and manipulation operations."""
    
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls']
    
    def load_data(self, uploaded_file) -> pd.DataFrame:
        """Load data from uploaded file."""
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                return pd.read_csv(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                return pd.read_excel(uploaded_file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def get_column_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get detailed information about DataFrame columns."""
        info = {}
        
        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'unique_count': df[col].nunique(),
                'is_numeric': pd.api.types.is_numeric_dtype(df[col]),
                'is_categorical': pd.api.types.is_categorical_dtype(df[col]),
                'is_datetime': pd.api.types.is_datetime64_any_dtype(df[col])
            }
            
            if col_info['is_numeric']:
                col_info.update({
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'mean': df[col].mean(),
                    'median': df[col].median(),
                    'std': df[col].std()
                })
            
            info[col] = col_info
        
        return info
    
    def filter_data(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to DataFrame."""
        filtered_df = df.copy()
        
        for column, filter_config in filters.items():
            if column not in df.columns:
                continue
                
            filter_type = filter_config.get('type')
            filter_value = filter_config.get('value')
            
            if filter_type == 'equals':
                filtered_df = filtered_df[filtered_df[column] == filter_value]
            elif filter_type == 'contains':
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(filter_value, case=False, na=False)]
            elif filter_type == 'range':
                min_val, max_val = filter_value
                filtered_df = filtered_df[(filtered_df[column] >= min_val) & (filtered_df[column] <= max_val)]
            elif filter_type == 'in':
                filtered_df = filtered_df[filtered_df[column].isin(filter_value)]
            elif filter_type == 'not_null':
                filtered_df = filtered_df[filtered_df[column].notna()]
            elif filter_type == 'null':
                filtered_df = filtered_df[filtered_df[column].isna()]
        
        return filtered_df
    
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for the DataFrame."""
        stats = {
            'shape': df.shape,
            'memory_usage': df.memory_usage(deep=True).sum(),
            'dtypes': df.dtypes.value_counts().to_dict()
        }
        
        # Numeric columns statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            stats['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        # Categorical columns statistics
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            stats['categorical_summary'] = {}
            for col in categorical_cols:
                stats['categorical_summary'][col] = {
                    'unique_count': df[col].nunique(),
                    'top_values': df[col].value_counts().head(5).to_dict()
                }
        
        return stats
    
    def clean_data(self, df: pd.DataFrame, operations: List[str]) -> pd.DataFrame:
        """Apply data cleaning operations."""
        cleaned_df = df.copy()
        
        for operation in operations:
            if operation == 'drop_nulls':
                cleaned_df = cleaned_df.dropna()
            elif operation == 'fill_numeric_nulls':
                numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                cleaned_df[numeric_cols] = cleaned_df[numeric_cols].fillna(cleaned_df[numeric_cols].median())
            elif operation == 'fill_categorical_nulls':
                categorical_cols = cleaned_df.select_dtypes(include=['object']).columns
                cleaned_df[categorical_cols] = cleaned_df[categorical_cols].fillna('Unknown')
            elif operation == 'remove_duplicates':
                cleaned_df = cleaned_df.drop_duplicates()
            elif operation == 'strip_whitespace':
                categorical_cols = cleaned_df.select_dtypes(include=['object']).columns
                cleaned_df[categorical_cols] = cleaned_df[categorical_cols].apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        
        return cleaned_df
    
    def create_derived_columns(self, df: pd.DataFrame, derivations: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create derived columns based on specifications."""
        derived_df = df.copy()
        
        for derivation in derivations:
            name = derivation['name']
            operation = derivation['operation']
            columns = derivation['columns']
            
            if operation == 'sum':
                derived_df[name] = derived_df[columns].sum(axis=1)
            elif operation == 'mean':
                derived_df[name] = derived_df[columns].mean(axis=1)
            elif operation == 'multiply':
                derived_df[name] = derived_df[columns].prod(axis=1)
            elif operation == 'concatenate':
                derived_df[name] = derived_df[columns].apply(lambda x: ' '.join(x.astype(str)), axis=1)
            elif operation == 'bin':
                bins = derivation.get('bins', 5)
                derived_df[name] = pd.cut(derived_df[columns[0]], bins=bins, labels=False)
        
        return derived_df
    
    def export_data(self, df: pd.DataFrame, format: str = 'csv') -> bytes:
        """Export DataFrame to specified format."""
        if format == 'csv':
            return df.to_csv(index=False).encode('utf-8')
        elif format == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
