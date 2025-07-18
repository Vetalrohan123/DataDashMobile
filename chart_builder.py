import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Optional

class ChartBuilder:
    """Handles creation of various chart types using Plotly."""
    
    def __init__(self):
        self.chart_types = {
            'bar': self.create_bar_chart,
            'line': self.create_line_chart,
            'pie': self.create_pie_chart,
            'scatter': self.create_scatter_chart,
            'histogram': self.create_histogram,
            'box': self.create_box_plot,
            'heatmap': self.create_heatmap,
            'area': self.create_area_chart
        }
    
    def get_available_chart_types(self) -> List[str]:
        """Get list of available chart types."""
        return list(self.chart_types.keys())
    
    def create_chart(self, df: pd.DataFrame, chart_config: Dict[str, Any]) -> go.Figure:
        """Create a chart based on configuration."""
        chart_type = chart_config.get('type', 'bar')
        
        if chart_type not in self.chart_types:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        return self.chart_types[chart_type](df, chart_config)
    
    def create_bar_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create a bar chart."""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        color_col = config.get('color_column')
        
        if not x_col or not y_col:
            raise ValueError("Both x_column and y_column are required for bar chart")
        
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=config.get('title', f'{y_col} by {x_col}'),
            labels=config.get('labels', {}),
            orientation=config.get('orientation', 'v')
        )
        
        self._apply_common_styling(fig, config)
        return fig
    
    def create_line_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create a line chart."""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        color_col = config.get('color_column')
        
        if not x_col or not y_col:
            raise ValueError("Both x_column and y_column are required for line chart")
        
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=config.get('title', f'{y_col} over {x_col}'),
            labels=config.get('labels', {}),
            markers=config.get('markers', True)
        )
        
        self._apply_common_styling(fig, config)
        return fig
    
    def create_pie_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create a pie chart."""
        values_col = config.get('values_column')
        names_col = config.get('names_column')
        
        if not values_col or not names_col:
            raise ValueError("Both values_column and names_column are required for pie chart")
        
        fig = px.pie(
            df,
            values=values_col,
            names=names_col,
            title=config.get('title', f'{values_col} by {names_col}'),
            labels=config.get('labels', {}),
            hole=config.get('hole', 0)
        )
        
        self._apply_common_styling(fig, config)
        return fig
    
    def create_scatter_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create a scatter plot."""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        color_col = config.get('color_column')
        size_col = config.get('size_column')
        
        if not x_col or not y_col:
            raise ValueError("Both x_column and y_column are required for scatter plot")
        
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            size=size_col,
            title=config.get('title', f'{y_col} vs {x_col}'),
            labels=config.get('labels', {}),
            hover_data=config.get('hover_data', [])
        )
        
        self._apply_common_styling(fig, config)
        return fig
    
    def create_histogram(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create a histogram."""
        x_col = config.get('x_column')
        
        if not x_col:
            raise ValueError("x_column is required for histogram")
        
        fig = px.histogram(
            df,
            x=x_col,
            title=config.get('title', f'Distribution of {x_col}'),
            labels=config.get('labels', {}),
            nbins=config.get('bins', 30)
        )
        
        self._apply_common_styling(fig, config)
        return fig
    
    def create_box_plot(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create a box plot."""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        
        if not y_col:
            raise ValueError("y_column is required for box plot")
        
        fig = px.box(
            df,
            x=x_col,
            y=y_col,
            title=config.get('title', f'Box Plot of {y_col}'),
            labels=config.get('labels', {})
        )
        
        self._apply_common_styling(fig, config)
        return fig
    
    def create_heatmap(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create a heatmap."""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        z_col = config.get('z_column')
        
        if not all([x_col, y_col, z_col]):
            raise ValueError("x_column, y_column, and z_column are required for heatmap")
        
        # Create pivot table for heatmap
        pivot_df = df.pivot_table(values=z_col, index=y_col, columns=x_col, aggfunc='mean')
        
        fig = px.imshow(
            pivot_df,
            title=config.get('title', f'Heatmap of {z_col}'),
            labels=config.get('labels', {}),
            aspect='auto'
        )
        
        self._apply_common_styling(fig, config)
        return fig
    
    def create_area_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create an area chart."""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        color_col = config.get('color_column')
        
        if not x_col or not y_col:
            raise ValueError("Both x_column and y_column are required for area chart")
        
        fig = px.area(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=config.get('title', f'{y_col} over {x_col}'),
            labels=config.get('labels', {})
        )
        
        self._apply_common_styling(fig, config)
        return fig
    
    def _apply_common_styling(self, fig: go.Figure, config: Dict[str, Any]):
        """Apply common styling to charts."""
        # Update layout for mobile responsiveness
        fig.update_layout(
            font=dict(size=12),
            title_font_size=16,
            margin=dict(l=20, r=20, t=60, b=20),
            autosize=True,
            height=config.get('height', 400)
        )
        
        # Apply custom colors if provided
        if config.get('color_scheme'):
            fig.update_traces(marker_color=config['color_scheme'])
        
        # Update axes labels
        if config.get('x_label'):
            fig.update_xaxes(title_text=config['x_label'])
        if config.get('y_label'):
            fig.update_yaxes(title_text=config['y_label'])
        
        # Hide legend if specified
        if config.get('hide_legend'):
            fig.update_layout(showlegend=False)
    
    def get_chart_requirements(self, chart_type: str) -> Dict[str, Any]:
        """Get requirements for a specific chart type."""
        requirements = {
            'bar': {
                'required': ['x_column', 'y_column'],
                'optional': ['color_column', 'orientation']
            },
            'line': {
                'required': ['x_column', 'y_column'],
                'optional': ['color_column', 'markers']
            },
            'pie': {
                'required': ['values_column', 'names_column'],
                'optional': ['hole']
            },
            'scatter': {
                'required': ['x_column', 'y_column'],
                'optional': ['color_column', 'size_column', 'hover_data']
            },
            'histogram': {
                'required': ['x_column'],
                'optional': ['bins']
            },
            'box': {
                'required': ['y_column'],
                'optional': ['x_column']
            },
            'heatmap': {
                'required': ['x_column', 'y_column', 'z_column'],
                'optional': []
            },
            'area': {
                'required': ['x_column', 'y_column'],
                'optional': ['color_column']
            }
        }
        
        return requirements.get(chart_type, {'required': [], 'optional': []})
