import streamlit as st
import pandas as pd
import json
import os
from utils.data_handler import DataHandler
from utils.dashboard_manager import DashboardManager

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

# Initialize components
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

if 'dashboard_manager' not in st.session_state:
    st.session_state.dashboard_manager = DashboardManager()

st.title("⚙️ Settings & Configuration")

# Sidebar navigation
with st.sidebar:
    st.header("Settings Menu")
    
    setting_options = [
        "Data Management",
        "Dashboard Management",
        "Export & Import",
        "Application Settings",
        "Help & Documentation"
    ]
    
    selected_setting = st.selectbox("Select Setting Category", setting_options)

# Main content based on selected setting
if selected_setting == "Data Management":
    st.header("📊 Data Management")
    
    # Current data information
    if st.session_state.current_data is not None:
        df = st.session_state.current_data
        
        st.subheader("Current Dataset Information")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.metric("Total Rows", len(df))
            st.metric("Total Columns", len(df.columns))
        
        with info_col2:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            st.metric("Missing Values", df.isnull().sum().sum())
        
        with info_col3:
            st.metric("Duplicate Rows", df.duplicated().sum())
            st.metric("Numeric Columns", len(df.select_dtypes(include=['number']).columns))
        
        # Data cleaning options
        st.subheader("Data Cleaning Options")
        
        cleaning_col1, cleaning_col2 = st.columns(2)
        
        with cleaning_col1:
            st.markdown("**Missing Values**")
            
            if st.button("Remove Rows with Missing Values"):
                cleaned_df = df.dropna()
                st.session_state.current_data = cleaned_df
                st.success(f"Removed {len(df) - len(cleaned_df)} rows with missing values")
                st.rerun()
            
            if st.button("Fill Missing Values (Auto)"):
                cleaned_df = st.session_state.data_handler.clean_data(df, ['fill_numeric_nulls', 'fill_categorical_nulls'])
                st.session_state.current_data = cleaned_df
                st.success("Missing values filled automatically")
                st.rerun()
        
        with cleaning_col2:
            st.markdown("**Data Quality**")
            
            if st.button("Remove Duplicate Rows"):
                cleaned_df = df.drop_duplicates()
                st.session_state.current_data = cleaned_df
                st.success(f"Removed {len(df) - len(cleaned_df)} duplicate rows")
                st.rerun()
            
            if st.button("Strip Whitespace from Text"):
                cleaned_df = st.session_state.data_handler.clean_data(df, ['strip_whitespace'])
                st.session_state.current_data = cleaned_df
                st.success("Whitespace stripped from text columns")
                st.rerun()
        
        # Column management
        st.subheader("Column Management")
        
        # Select columns to keep
        selected_columns = st.multiselect(
            "Select columns to keep",
            df.columns.tolist(),
            default=df.columns.tolist()
        )
        
        if st.button("Apply Column Selection"):
            if selected_columns:
                st.session_state.current_data = df[selected_columns]
                st.success(f"Dataset now contains {len(selected_columns)} columns")
                st.rerun()
            else:
                st.warning("Please select at least one column")
        
        # Data type conversions
        st.subheader("Data Type Conversions")
        
        for col in df.columns:
            col_container = st.container()
            with col_container:
                conversion_col1, conversion_col2 = st.columns(2)
                
                with conversion_col1:
                    st.text(f"{col} ({df[col].dtype})")
                
                with conversion_col2:
                    new_type = st.selectbox(
                        f"Convert to",
                        ["No Change", "Numeric", "Text", "Category", "Datetime"],
                        key=f"convert_{col}"
                    )
                    
                    if new_type != "No Change":
                        if st.button(f"Convert {col}", key=f"btn_convert_{col}"):
                            try:
                                if new_type == "Numeric":
                                    df[col] = pd.to_numeric(df[col], errors='coerce')
                                elif new_type == "Text":
                                    df[col] = df[col].astype(str)
                                elif new_type == "Category":
                                    df[col] = df[col].astype('category')
                                elif new_type == "Datetime":
                                    df[col] = pd.to_datetime(df[col], errors='coerce')
                                
                                st.session_state.current_data = df
                                st.success(f"Converted {col} to {new_type}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error converting {col}: {str(e)}")
    
    else:
        st.info("No data loaded. Please upload data first.")

elif selected_setting == "Dashboard Management":
    st.header("📊 Dashboard Management")
    
    # Dashboard list
    dashboards = st.session_state.dashboard_manager.get_dashboard_list()
    
    if dashboards:
        st.subheader("Saved Dashboards")
        
        for dashboard in dashboards:
            dashboard_info = st.session_state.dashboard_manager.get_dashboard_info(dashboard)
            
            if dashboard_info:
                with st.expander(f"📊 {dashboard}"):
                    info_col1, info_col2, info_col3 = st.columns(3)
                    
                    with info_col1:
                        st.metric("Charts", dashboard_info['chart_count'])
                        st.metric("Has Filters", "Yes" if dashboard_info['has_filters'] else "No")
                    
                    with info_col2:
                        metadata = dashboard_info['metadata']
                        st.text(f"Created: {metadata.get('created_at', 'Unknown')[:10]}")
                        st.text(f"Modified: {metadata.get('last_modified', 'Unknown')[:10]}")
                    
                    with info_col3:
                        # Dashboard actions
                        if st.button(f"Load {dashboard}", key=f"load_{dashboard}"):
                            loaded_config = st.session_state.dashboard_manager.load_dashboard(dashboard)
                            if loaded_config:
                                st.session_state.current_dashboard = loaded_config
                                st.session_state.dashboard_charts = loaded_config.get('charts', [])
                                st.success(f"Dashboard '{dashboard}' loaded successfully!")
                        
                        if st.button(f"Delete {dashboard}", key=f"delete_{dashboard}"):
                            if st.session_state.dashboard_manager.delete_dashboard(dashboard):
                                st.success(f"Dashboard '{dashboard}' deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete dashboard")
    
    else:
        st.info("No saved dashboards found.")
    
    # Dashboard operations
    st.subheader("Dashboard Operations")
    
    operation_col1, operation_col2 = st.columns(2)
    
    with operation_col1:
        st.markdown("**Create New Dashboard**")
        
        new_dashboard_name = st.text_input("New Dashboard Name")
        
        if st.button("Create Dashboard"):
            if new_dashboard_name:
                new_dashboard = st.session_state.dashboard_manager.create_default_dashboard()
                if st.session_state.dashboard_manager.save_dashboard(new_dashboard_name, new_dashboard):
                    st.success(f"Dashboard '{new_dashboard_name}' created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create dashboard")
            else:
                st.warning("Please enter a dashboard name")
    
    with operation_col2:
        st.markdown("**Duplicate Dashboard**")
        
        if dashboards:
            source_dashboard = st.selectbox("Select dashboard to duplicate", dashboards)
            target_dashboard = st.text_input("New dashboard name")
            
            if st.button("Duplicate Dashboard"):
                if target_dashboard:
                    if st.session_state.dashboard_manager.duplicate_dashboard(source_dashboard, target_dashboard):
                        st.success(f"Dashboard duplicated as '{target_dashboard}'!")
                        st.rerun()
                    else:
                        st.error("Failed to duplicate dashboard")
                else:
                    st.warning("Please enter a new dashboard name")

elif selected_setting == "Export & Import":
    st.header("📤 Export & Import")
    
    # Export section
    st.subheader("Export Data")
    
    if st.session_state.current_data is not None:
        df = st.session_state.current_data
        
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            st.markdown("**Export Current Data**")
            
            export_format = st.selectbox("Export Format", ["CSV", "Excel"])
            
            if st.button("Export Data"):
                try:
                    if export_format == "CSV":
                        data = st.session_state.data_handler.export_data(df, 'csv')
                        st.download_button(
                            label="Download CSV",
                            data=data,
                            file_name=f"data_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        data = st.session_state.data_handler.export_data(df, 'excel')
                        st.download_button(
                            label="Download Excel",
                            data=data,
                            file_name=f"data_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")
        
        with export_col2:
            st.markdown("**Export Dashboard**")
            
            dashboards = st.session_state.dashboard_manager.get_dashboard_list()
            
            if dashboards:
                selected_dashboard = st.selectbox("Select Dashboard", dashboards)
                
                if st.button("Export Dashboard"):
                    dashboard_data = st.session_state.dashboard_manager.export_dashboard(selected_dashboard)
                    if dashboard_data:
                        st.download_button(
                            label="Download Dashboard JSON",
                            data=dashboard_data,
                            file_name=f"{selected_dashboard}_dashboard.json",
                            mime="application/json"
                        )
            else:
                st.info("No dashboards to export")
    
    else:
        st.info("No data loaded to export")
    
    # Import section
    st.subheader("Import Data")
    
    import_col1, import_col2 = st.columns(2)
    
    with import_col1:
        st.markdown("**Import Dashboard**")
        
        uploaded_dashboard = st.file_uploader(
            "Upload Dashboard JSON",
            type=['json'],
            key="dashboard_import"
        )
        
        if uploaded_dashboard:
            dashboard_name = st.text_input("Dashboard Name", value="Imported Dashboard")
            
            if st.button("Import Dashboard"):
                if st.session_state.dashboard_manager.import_dashboard(uploaded_dashboard, dashboard_name):
                    st.success(f"Dashboard imported as '{dashboard_name}'!")
                    st.rerun()
                else:
                    st.error("Failed to import dashboard")
    
    with import_col2:
        st.markdown("**Replace Current Data**")
        
        uploaded_data = st.file_uploader(
            "Upload New Data File",
            type=['csv', 'xlsx', 'xls'],
            key="data_import"
        )
        
        if uploaded_data:
            if st.button("Replace Data"):
                try:
                    new_data = st.session_state.data_handler.load_data(uploaded_data)
                    st.session_state.current_data = new_data
                    st.success(f"Data replaced successfully! New shape: {new_data.shape}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load data: {str(e)}")

elif selected_setting == "Application Settings":
    st.header("⚙️ Application Settings")
    
    # Performance settings
    st.subheader("Performance Settings")
    
    perf_col1, perf_col2 = st.columns(2)
    
    with perf_col1:
        st.markdown("**Chart Settings**")
        
        default_chart_height = st.slider("Default Chart Height", 200, 800, 400)
        max_data_points = st.slider("Max Data Points for Charts", 1000, 10000, 5000)
        
        if st.button("Apply Performance Settings"):
            # Store in session state
            st.session_state.chart_height = default_chart_height
            st.session_state.max_data_points = max_data_points
            st.success("Performance settings applied!")
    
    with perf_col2:
        st.markdown("**Data Processing**")
        
        auto_data_types = st.checkbox("Auto-detect Data Types", value=True)
        cache_data = st.checkbox("Cache Data Operations", value=True)
        
        if st.button("Apply Data Settings"):
            st.session_state.auto_data_types = auto_data_types
            st.session_state.cache_data = cache_data
            st.success("Data settings applied!")
    
    # Display settings
    st.subheader("Display Settings")
    
    display_col1, display_col2 = st.columns(2)
    
    with display_col1:
        st.markdown("**Table Display**")
        
        max_rows_display = st.slider("Max Rows to Display", 10, 100, 50)
        show_data_types = st.checkbox("Show Data Types in Tables", value=True)
        
        if st.button("Apply Display Settings"):
            st.session_state.max_rows_display = max_rows_display
            st.session_state.show_data_types = show_data_types
            st.success("Display settings applied!")
    
    with display_col2:
        st.markdown("**Color Scheme**")
        
        color_scheme = st.selectbox(
            "Chart Color Scheme",
            ["Default", "Blues", "Reds", "Greens", "Viridis", "Plasma"]
        )
        
        theme = st.selectbox(
            "Application Theme",
            ["Light", "Dark", "Auto"]
        )
        
        if st.button("Apply Theme Settings"):
            st.session_state.color_scheme = color_scheme
            st.session_state.theme = theme
            st.success("Theme settings applied!")

elif selected_setting == "Help & Documentation":
    st.header("📚 Help & Documentation")
    
    help_col1, help_col2 = st.columns(2)
    
    with help_col1:
        st.subheader("Getting Started")
        
        st.markdown("""
        #### 📊 Data Upload
        1. Go to the home page
        2. Click "Choose file" to upload CSV or Excel files
        3. Review the data preview and statistics
        4. Use the quick actions to start analyzing
        
        #### 🎨 Dashboard Builder
        1. Navigate to the Dashboard Builder page
        2. Select chart type and configure columns
        3. Customize chart appearance and settings
        4. Add charts to your dashboard
        5. Save your dashboard for future use
        
        #### 📈 Reports
        1. Go to the Reports page
        2. Configure report sections and preferences
        3. Generate comprehensive reports
        4. Export reports in HTML format
        """)
    
    with help_col2:
        st.subheader("Features Guide")
        
        st.markdown("""
        #### 🔧 Data Management
        - **Data Cleaning**: Remove nulls, duplicates, and whitespace
        - **Column Management**: Select, rename, and convert data types
        - **Filtering**: Apply filters to focus on specific data
        
        #### 📊 Visualization Types
        - **Bar Charts**: Compare categories
        - **Line Charts**: Show trends over time
        - **Pie Charts**: Show proportions
        - **Scatter Plots**: Show relationships
        - **Histograms**: Show distributions
        - **Box Plots**: Show statistical distributions
        - **Heatmaps**: Show correlations
        
        #### 💾 Data Export
        - **CSV Export**: Standard comma-separated format
        - **Excel Export**: Formatted spreadsheet
        - **Dashboard Export**: JSON configuration file
        - **Report Export**: HTML report format
        """)
    
    # FAQ section
    st.subheader("Frequently Asked Questions")
    
    with st.expander("❓ What file formats are supported?"):
        st.markdown("""
        The application supports:
        - **CSV files** (.csv)
        - **Excel files** (.xlsx, .xls)
        
        Make sure your data has proper column headers and is formatted consistently.
        """)
    
    with st.expander("❓ How do I handle missing data?"):
        st.markdown("""
        You can handle missing data in several ways:
        1. **Remove rows** with missing values
        2. **Fill missing values** automatically (numeric columns get median, text columns get 'Unknown')
        3. **Manual replacement** using data cleaning tools
        
        Go to Settings > Data Management for these options.
        """)
    
    with st.expander("❓ Can I save my work?"):
        st.markdown("""
        Yes! You can save:
        - **Dashboard configurations** as JSON files
        - **Data exports** as CSV or Excel files
        - **Reports** as HTML files
        
        Use the export options in each section to save your work.
        """)
    
    with st.expander("❓ How do I create effective charts?"):
        st.markdown("""
        Chart selection tips:
        - **Bar charts**: Best for comparing categories
        - **Line charts**: Best for time series data
        - **Pie charts**: Best for showing proportions (use sparingly)
        - **Scatter plots**: Best for showing relationships between variables
        - **Histograms**: Best for showing data distributions
        
        Always consider your audience and the story you want to tell with your data.
        """)
    
    # Version information
    st.subheader("Version Information")
    
    st.info("""
    **Analytics Dashboard Tool v1.0**
    
    Built with:
    - Streamlit for web interface
    - Plotly for interactive visualizations
    - Pandas for data processing
    - Python for backend logic
    
    For support or feature requests, please contact your administrator.
    """)

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
    .stButton button {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)
