import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import io
import base64

class ReportGenerator:
    """Generates reports with key metrics and visualizations."""
    
    def __init__(self):
        self.report_sections = {
            'summary': self._generate_summary_section,
            'statistics': self._generate_statistics_section,
            'charts': self._generate_charts_section,
            'insights': self._generate_insights_section
        }
    
    def generate_report(self, df: pd.DataFrame, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive report."""
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_shape': df.shape,
                'title': report_config.get('title', 'Data Analysis Report')
            },
            'sections': {}
        }
        
        # Generate requested sections
        sections = report_config.get('sections', ['summary', 'statistics', 'charts'])
        
        for section in sections:
            if section in self.report_sections:
                try:
                    report['sections'][section] = self.report_sections[section](df, report_config)
                except Exception as e:
                    st.error(f"Error generating {section} section: {str(e)}")
                    report['sections'][section] = {'error': str(e)}
        
        return report
    
    def _generate_summary_section(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary section."""
        summary = {
            'title': 'Data Summary',
            'metrics': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
                'missing_values': df.isnull().sum().sum(),
                'duplicate_rows': df.duplicated().sum()
            },
            'column_types': {
                'numeric': len(df.select_dtypes(include=['number']).columns),
                'categorical': len(df.select_dtypes(include=['object']).columns),
                'datetime': len(df.select_dtypes(include=['datetime']).columns)
            }
        }
        
        # Add data quality metrics
        summary['data_quality'] = {
            'completeness': f"{((df.size - df.isnull().sum().sum()) / df.size * 100):.1f}%",
            'uniqueness': f"{(df.nunique().sum() / df.size * 100):.1f}%"
        }
        
        return summary
    
    def _generate_statistics_section(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistics section."""
        stats = {
            'title': 'Statistical Analysis',
            'numeric_stats': {},
            'categorical_stats': {}
        }
        
        # Numeric columns statistics
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats['numeric_stats'] = df[numeric_cols].describe().to_dict()
        
        # Categorical columns statistics
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                stats['categorical_stats'][col] = {
                    'unique_values': df[col].nunique(),
                    'top_values': df[col].value_counts().head(5).to_dict(),
                    'missing_values': df[col].isnull().sum()
                }
        
        # Correlation analysis for numeric columns
        if len(numeric_cols) > 1:
            stats['correlations'] = df[numeric_cols].corr().to_dict()
        
        return stats
    
    def _generate_charts_section(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate charts section."""
        charts = {
            'title': 'Data Visualizations',
            'charts': []
        }
        
        # Auto-generate charts based on data types
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Distribution charts for numeric columns
        for col in numeric_cols[:3]:  # Limit to first 3 columns
            if df[col].nunique() > 1:
                fig = px.histogram(df, x=col, title=f'Distribution of {col}')
                charts['charts'].append({
                    'type': 'histogram',
                    'title': f'Distribution of {col}',
                    'column': col,
                    'figure': fig
                })
        
        # Bar charts for categorical columns
        for col in categorical_cols[:3]:  # Limit to first 3 columns
            if df[col].nunique() <= 20:  # Only for columns with reasonable unique values
                value_counts = df[col].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values, 
                           title=f'Top Values in {col}')
                charts['charts'].append({
                    'type': 'bar',
                    'title': f'Top Values in {col}',
                    'column': col,
                    'figure': fig
                })
        
        # Correlation heatmap for numeric columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                          title='Correlation Matrix')
            charts['charts'].append({
                'type': 'heatmap',
                'title': 'Correlation Matrix',
                'figure': fig
            })
        
        return charts
    
    def _generate_insights_section(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights section."""
        insights = {
            'title': 'Key Insights',
            'insights': []
        }
        
        # Data quality insights
        missing_pct = (df.isnull().sum() / len(df) * 100)
        high_missing = missing_pct[missing_pct > 10].index.tolist()
        if high_missing:
            insights['insights'].append({
                'type': 'data_quality',
                'severity': 'warning',
                'title': 'High Missing Values',
                'description': f"Columns with >10% missing values: {', '.join(high_missing)}"
            })
        
        # Duplicate rows insight
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            insights['insights'].append({
                'type': 'data_quality',
                'severity': 'info',
                'title': 'Duplicate Rows',
                'description': f"Found {duplicate_count} duplicate rows ({duplicate_count/len(df)*100:.1f}%)"
            })
        
        # Numeric columns insights
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if df[col].nunique() == 1:
                insights['insights'].append({
                    'type': 'column_analysis',
                    'severity': 'info',
                    'title': f'Constant Column: {col}',
                    'description': f"Column '{col}' has only one unique value"
                })
            
            # Check for outliers (simple IQR method)
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
            if len(outliers) > 0:
                insights['insights'].append({
                    'type': 'outliers',
                    'severity': 'info',
                    'title': f'Outliers in {col}',
                    'description': f"Found {len(outliers)} potential outliers ({len(outliers)/len(df)*100:.1f}%)"
                })
        
        # Categorical columns insights
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            unique_count = df[col].nunique()
            if unique_count == len(df):
                insights['insights'].append({
                    'type': 'column_analysis',
                    'severity': 'info',
                    'title': f'Unique Column: {col}',
                    'description': f"Column '{col}' has all unique values (potential identifier)"
                })
            elif unique_count > len(df) * 0.5:
                insights['insights'].append({
                    'type': 'column_analysis',
                    'severity': 'info',
                    'title': f'High Cardinality: {col}',
                    'description': f"Column '{col}' has {unique_count} unique values ({unique_count/len(df)*100:.1f}%)"
                })
        
        return insights
    
    def export_report_html(self, report: Dict[str, Any]) -> str:
        """Export report as HTML."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report['metadata']['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f0f0f0; border-radius: 5px; }}
                .insight {{ margin: 10px 0; padding: 10px; border-left: 4px solid #007bff; background: #f8f9fa; }}
                .warning {{ border-left-color: #ffc107; }}
                .error {{ border-left-color: #dc3545; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report['metadata']['title']}</h1>
                <p>Generated on: {report['metadata']['generated_at']}</p>
                <p>Data Shape: {report['metadata']['data_shape'][0]} rows × {report['metadata']['data_shape'][1]} columns</p>
            </div>
        """
        
        # Add sections
        for section_name, section_data in report['sections'].items():
            if 'error' in section_data:
                html += f"""
                <div class="section">
                    <h2>{section_data.get('title', section_name.title())}</h2>
                    <div class="insight error">Error: {section_data['error']}</div>
                </div>
                """
                continue
            
            html += f'<div class="section"><h2>{section_data.get("title", section_name.title())}</h2>'
            
            if section_name == 'summary':
                html += self._format_summary_html(section_data)
            elif section_name == 'statistics':
                html += self._format_statistics_html(section_data)
            elif section_name == 'insights':
                html += self._format_insights_html(section_data)
            
            html += '</div>'
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _format_summary_html(self, summary: Dict[str, Any]) -> str:
        """Format summary section as HTML."""
        html = "<h3>Key Metrics</h3>"
        for key, value in summary['metrics'].items():
            html += f'<div class="metric"><strong>{key.replace("_", " ").title()}:</strong> {value}</div>'
        
        html += "<h3>Column Types</h3>"
        for key, value in summary['column_types'].items():
            html += f'<div class="metric"><strong>{key.title()}:</strong> {value}</div>'
        
        html += "<h3>Data Quality</h3>"
        for key, value in summary['data_quality'].items():
            html += f'<div class="metric"><strong>{key.title()}:</strong> {value}</div>'
        
        return html
    
    def _format_statistics_html(self, stats: Dict[str, Any]) -> str:
        """Format statistics section as HTML."""
        html = ""
        
        if stats['numeric_stats']:
            html += "<h3>Numeric Statistics</h3>"
            # Convert to table format
            html += "<table><tr><th>Statistic</th>"
            for col in stats['numeric_stats'].keys():
                html += f"<th>{col}</th>"
            html += "</tr>"
            
            for stat in ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']:
                html += f"<tr><td>{stat}</td>"
                for col in stats['numeric_stats'].keys():
                    value = stats['numeric_stats'][col].get(stat, 'N/A')
                    if isinstance(value, float):
                        value = f"{value:.2f}"
                    html += f"<td>{value}</td>"
                html += "</tr>"
            html += "</table>"
        
        return html
    
    def _format_insights_html(self, insights: Dict[str, Any]) -> str:
        """Format insights section as HTML."""
        html = ""
        
        for insight in insights['insights']:
            severity_class = insight.get('severity', 'info')
            html += f"""
            <div class="insight {severity_class}">
                <strong>{insight['title']}</strong><br>
                {insight['description']}
            </div>
            """
        
        return html
    
    def export_report_pdf(self, report: Dict[str, Any]) -> bytes:
        """Export report as PDF (placeholder - would need additional libraries)."""
        # This would require libraries like reportlab or weasyprint
        # For now, return HTML as bytes
        html = self.export_report_html(report)
        return html.encode('utf-8')
