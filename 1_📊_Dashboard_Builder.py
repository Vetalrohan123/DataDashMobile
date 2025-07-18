import streamlit as st
import pandas as pd
import plotly.express as px
from utils.chart_builder import ChartBuilder
from utils.dashboard_manager import DashboardManager
import json

st.set_page_config(
    page_title="Dashboard Builder",
    page_icon="📊",
    layout="wide"
)

# Initialize components
if 'chart_builder' not in st.session_state:
    st.session_state.chart_builder = ChartBuilder()

if 'dashboard_manager' not in st.session_state:
    st.session_state.dashboard_manager = DashboardManager()

if 'current_dashboard' not in st.session_state:
    st.session_state.current_dashboard = st.session_state.dashboard_manager.create_default_dashboard()

if 'dashboard_charts' not in st.session_state:
    st.session_state.dashboard_charts = []

st.title("📊 Dashboard Builder")

# Check if data is loaded
if st.session_state.current_data is None:
    st.warning("⚠️ No data loaded. Please upload data first.")
    if st.button("Go to Home"):
        st.switch_page("app.py")
    st.stop()

df = st.session_state.current_data

# Sidebar for dashboard management
with st.sidebar:
    st.header("Dashboard Management")
    
    # Save current dashboard
    dashboard_name = st.text_input("Dashboard Name", value="My Dashboard")
    if st.button("💾 Save Dashboard"):
        dashboard_config = {
            'layout': st.session_state.current_dashboard['layout'],
            'charts': st.session_state.dashboard_charts,
            'filters': st.session_state.current_dashboard.get('filters', {})
        }
        
        if st.session_state.dashboard_manager.save_dashboard(dashboard_name, dashboard_config):
            st.success(f"Dashboard '{dashboard_name}' saved successfully!")
        else:
            st.error("Failed to save dashboard")
    
    # Load existing dashboard
    st.markdown("---")
    st.subheader("Load Dashboard")
    existing_dashboards = st.session_state.dashboard_manager.get_dashboard_list()
    
    if existing_dashboards:
        selected_dashboard = st.selectbox("Select Dashboard", existing_dashboards)
        if st.button("📂 Load Dashboard"):
            loaded_config = st.session_state.dashboard_manager.load_dashboard(selected_dashboard)
            if loaded_config:
                st.session_state.current_dashboard = loaded_config
                st.session_state.dashboard_charts = loaded_config.get('charts', [])
                st.success(f"Dashboard '{selected_dashboard}' loaded successfully!")
                st.rerun()
    else:
        st.info("No saved dashboards found")
    
    # Export dashboard
    st.markdown("---")
    st.subheader("Export Dashboard")
    if st.button("📤 Export as JSON"):
        if st.session_state.dashboard_charts:
            dashboard_config = {
                'layout': st.session_state.current_dashboard['layout'],
                'charts': st.session_state.dashboard_charts,
                'filters': st.session_state.current_dashboard.get('filters', {})
            }
            
            json_str = json.dumps(dashboard_config, indent=2)
            st.download_button(
                label="Download Dashboard JSON",
                data=json_str,
                file_name=f"{dashboard_name}.json",
                mime="application/json"
            )
        else:
            st.warning("No charts to export")

# Main dashboard builder interface
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🎨 Chart Builder")
    
    # Chart type selection
    chart_type = st.selectbox(
        "Chart Type",
        st.session_state.chart_builder.get_available_chart_types(),
        format_func=lambda x: x.title()
    )
    
    # Get chart requirements
    requirements = st.session_state.chart_builder.get_chart_requirements(chart_type)
    
    # Column selection based on chart type
    chart_config = {'type': chart_type}
    
    # Get numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    all_cols = df.columns.tolist()
    
    # Required fields
    for field in requirements['required']:
        if field == 'x_column':
            chart_config['x_column'] = st.selectbox("X-axis Column", all_cols)
        elif field == 'y_column':
            chart_config['y_column'] = st.selectbox("Y-axis Column", numeric_cols)
        elif field == 'values_column':
            chart_config['values_column'] = st.selectbox("Values Column", numeric_cols)
        elif field == 'names_column':
            chart_config['names_column'] = st.selectbox("Names Column", categorical_cols)
        elif field == 'z_column':
            chart_config['z_column'] = st.selectbox("Z-axis Column", numeric_cols)
    
    # Optional fields
    for field in requirements['optional']:
        if field == 'color_column':
            chart_config['color_column'] = st.selectbox("Color Column (Optional)", [None] + categorical_cols)
        elif field == 'size_column':
            chart_config['size_column'] = st.selectbox("Size Column (Optional)", [None] + numeric_cols)
        elif field == 'orientation':
            chart_config['orientation'] = st.selectbox("Orientation", ['v', 'h'])
        elif field == 'markers':
            chart_config['markers'] = st.checkbox("Show Markers", value=True)
        elif field == 'bins':
            chart_config['bins'] = st.slider("Number of Bins", 5, 100, 30)
        elif field == 'hole':
            chart_config['hole'] = st.slider("Hole Size", 0.0, 0.8, 0.0)
    
    # Chart customization
    st.markdown("---")
    st.subheader("Chart Customization")
    
    chart_config['title'] = st.text_input("Chart Title", value=f"{chart_type.title()} Chart")
    chart_config['height'] = st.slider("Chart Height", 200, 800, 400)
    
    # Color scheme
    color_schemes = {
        'Default': None,
        'Blues': px.colors.sequential.Blues,
        'Reds': px.colors.sequential.Reds,
        'Greens': px.colors.sequential.Greens,
        'Viridis': px.colors.sequential.Viridis
    }
    
    selected_color_scheme = st.selectbox("Color Scheme", list(color_schemes.keys()))
    if selected_color_scheme != 'Default':
        chart_config['color_scheme'] = color_schemes[selected_color_scheme]
    
    # Add chart button
    if st.button("➕ Add Chart to Dashboard"):
        try:
            # Create the chart
            fig = st.session_state.chart_builder.create_chart(df, chart_config)
            
            # Add to dashboard
            chart_id = f"chart_{len(st.session_state.dashboard_charts) + 1}"
            st.session_state.dashboard_charts.append({
                'id': chart_id,
                'type': chart_type,
                'config': chart_config,
                'figure': fig
            })
            
            st.success(f"Chart added to dashboard!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")

with col2:
    st.header("📊 Dashboard Preview")
    
    if st.session_state.dashboard_charts:
        # Display charts in grid layout
        charts_per_row = 2
        
        for i in range(0, len(st.session_state.dashboard_charts), charts_per_row):
            cols = st.columns(charts_per_row)
            
            for j in range(charts_per_row):
                chart_idx = i + j
                if chart_idx < len(st.session_state.dashboard_charts):
                    chart = st.session_state.dashboard_charts[chart_idx]
                    
                    with cols[j]:
                        # Chart controls
                        col_control, col_delete = st.columns([3, 1])
                        
                        with col_control:
                            st.markdown(f"**{chart['config']['title']}**")
                        
                        with col_delete:
                            if st.button("🗑️", key=f"delete_{chart['id']}"):
                                st.session_state.dashboard_charts.pop(chart_idx)
                                st.rerun()
                        
                        # Display chart
                        st.plotly_chart(chart['figure'], use_container_width=True)
    else:
        st.info("No charts added yet. Use the chart builder to add charts to your dashboard.")

# Data filtering section
st.markdown("---")
st.header("🔍 Data Filters")

# Global filters
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    st.subheader("Column Filters")
    
    # Select column to filter
    filter_column = st.selectbox("Select Column to Filter", [None] + df.columns.tolist())
    
    if filter_column:
        column_type = df[filter_column].dtype
        
        if pd.api.types.is_numeric_dtype(df[filter_column]):
            # Numeric filter
            min_val = float(df[filter_column].min())
            max_val = float(df[filter_column].max())
            
            filter_range = st.slider(
                f"Filter {filter_column}",
                min_val, max_val, (min_val, max_val)
            )
            
            if st.button("Apply Numeric Filter"):
                filtered_df = df[(df[filter_column] >= filter_range[0]) & 
                               (df[filter_column] <= filter_range[1])]
                st.session_state.current_data = filtered_df
                st.success(f"Filter applied! New shape: {filtered_df.shape}")
                st.rerun()
        
        else:
            # Categorical filter
            unique_values = df[filter_column].unique()
            selected_values = st.multiselect(
                f"Select {filter_column} values",
                unique_values,
                default=unique_values
            )
            
            if st.button("Apply Categorical Filter"):
                filtered_df = df[df[filter_column].isin(selected_values)]
                st.session_state.current_data = filtered_df
                st.success(f"Filter applied! New shape: {filtered_df.shape}")
                st.rerun()

with filter_col2:
    st.subheader("Data Operations")
    
    # Remove null values
    if st.button("Remove Null Values"):
        filtered_df = df.dropna()
        st.session_state.current_data = filtered_df
        st.success(f"Null values removed! New shape: {filtered_df.shape}")
        st.rerun()
    
    # Remove duplicates
    if st.button("Remove Duplicates"):
        filtered_df = df.drop_duplicates()
        st.session_state.current_data = filtered_df
        st.success(f"Duplicates removed! New shape: {filtered_df.shape}")
        st.rerun()
    
    # Reset filters
    if st.button("Reset All Filters"):
        # This would need to restore original data
        st.info("Reset functionality would restore original data")

with filter_col3:
    st.subheader("Current Data Info")
    
    st.metric("Total Rows", len(df))
    st.metric("Total Columns", len(df.columns))
    st.metric("Missing Values", df.isnull().sum().sum())
    st.metric("Duplicates", df.duplicated().sum())

# Mobile-responsive adjustments
st.markdown("""
<style>
@media (max-width: 768px) {
    .stColumn {
        width: 100% !important;
    }
    .stSelectbox {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)
