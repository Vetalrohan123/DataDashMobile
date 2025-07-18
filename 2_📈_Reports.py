import streamlit as st
import pandas as pd
from utils.report_generator import ReportGenerator
from utils.data_handler import DataHandler
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

st.set_page_config(
    page_title="Reports",
    page_icon="📈",
    layout="wide"
)

# Initialize components
if 'report_generator' not in st.session_state:
    st.session_state.report_generator = ReportGenerator()

if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

st.title("📈 Reports & Analytics")

# Check if data is loaded
if st.session_state.current_data is None:
    st.warning("⚠️ No data loaded. Please upload data first.")
    if st.button("Go to Home"):
        st.switch_page("app.py")
    st.stop()

df = st.session_state.current_data

# Sidebar for report configuration
with st.sidebar:
    st.header("Report Configuration")
    
    # Report title
    report_title = st.text_input("Report Title", value="Data Analysis Report")
    
    # Report sections
    st.subheader("Report Sections")
    include_summary = st.checkbox("📊 Summary", value=True)
    include_statistics = st.checkbox("📈 Statistics", value=True)
    include_charts = st.checkbox("📊 Charts", value=True)
    include_insights = st.checkbox("💡 Insights", value=True)
    
    # Chart preferences
    st.subheader("Chart Preferences")
    max_charts = st.slider("Maximum Charts per Section", 1, 10, 3)
    chart_height = st.slider("Chart Height", 200, 600, 400)
    
    # Generate report button
    if st.button("📋 Generate Report"):
        sections = []
        if include_summary:
            sections.append('summary')
        if include_statistics:
            sections.append('statistics')
        if include_charts:
            sections.append('charts')
        if include_insights:
            sections.append('insights')
        
        report_config = {
            'title': report_title,
            'sections': sections,
            'max_charts': max_charts,
            'chart_height': chart_height
        }
        
        with st.spinner("Generating report..."):
            report = st.session_state.report_generator.generate_report(df, report_config)
            st.session_state.current_report = report
            st.success("Report generated successfully!")
            st.rerun()

# Main report display
if 'current_report' in st.session_state:
    report = st.session_state.current_report
    
    # Report header
    st.header(report['metadata']['title'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Generated", report['metadata']['generated_at'][:10])
    with col2:
        st.metric("Data Shape", f"{report['metadata']['data_shape'][0]} × {report['metadata']['data_shape'][1]}")
    with col3:
        st.metric("Sections", len(report['sections']))
    
    # Export options
    st.markdown("---")
    st.subheader("📤 Export Options")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.button("📄 Export as HTML"):
            html_content = st.session_state.report_generator.export_report_html(report)
            st.download_button(
                label="Download HTML Report",
                data=html_content,
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
    
    with export_col2:
        if st.button("📊 Export Data as CSV"):
            csv_data = st.session_state.data_handler.export_data(df, 'csv')
            st.download_button(
                label="Download CSV Data",
                data=csv_data,
                file_name=f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with export_col3:
        if st.button("📁 Export Data as Excel"):
            excel_data = st.session_state.data_handler.export_data(df, 'excel')
            st.download_button(
                label="Download Excel Data",
                data=excel_data,
                file_name=f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Display report sections
    st.markdown("---")
    
    # Summary section
    if 'summary' in report['sections']:
        st.header("📊 Data Summary")
        summary = report['sections']['summary']
        
        # Key metrics
        st.subheader("Key Metrics")
        metric_cols = st.columns(5)
        
        metrics = summary['metrics']
        metric_items = list(metrics.items())
        
        for i, (key, value) in enumerate(metric_items):
            with metric_cols[i % 5]:
                st.metric(key.replace('_', ' ').title(), value)
        
        # Column types
        st.subheader("Column Types")
        col_type_cols = st.columns(3)
        
        for i, (key, value) in enumerate(summary['column_types'].items()):
            with col_type_cols[i]:
                st.metric(key.title(), value)
        
        # Data quality
        st.subheader("Data Quality")
        quality_cols = st.columns(2)
        
        for i, (key, value) in enumerate(summary['data_quality'].items()):
            with quality_cols[i]:
                st.metric(key.title(), value)
    
    # Statistics section
    if 'statistics' in report['sections']:
        st.header("📈 Statistical Analysis")
        stats = report['sections']['statistics']
        
        # Numeric statistics
        if stats['numeric_stats']:
            st.subheader("Numeric Statistics")
            numeric_df = pd.DataFrame(stats['numeric_stats'])
            st.dataframe(numeric_df.round(2), use_container_width=True)
        
        # Categorical statistics
        if stats['categorical_stats']:
            st.subheader("Categorical Statistics")
            
            for col, col_stats in stats['categorical_stats'].items():
                with st.expander(f"📊 {col}"):
                    stat_col1, stat_col2 = st.columns(2)
                    
                    with stat_col1:
                        st.metric("Unique Values", col_stats['unique_values'])
                        st.metric("Missing Values", col_stats['missing_values'])
                    
                    with stat_col2:
                        st.markdown("**Top Values:**")
                        for value, count in col_stats['top_values'].items():
                            st.text(f"• {value}: {count}")
        
        # Correlations
        if 'correlations' in stats:
            st.subheader("Correlation Matrix")
            corr_df = pd.DataFrame(stats['correlations'])
            
            # Create correlation heatmap
            fig = px.imshow(
                corr_df,
                text_auto=True,
                aspect="auto",
                title="Correlation Matrix",
                color_continuous_scale="RdBu"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    # Charts section
    if 'charts' in report['sections']:
        st.header("📊 Data Visualizations")
        charts = report['sections']['charts']
        
        # Display charts in grid
        chart_cols = st.columns(2)
        
        for i, chart in enumerate(charts['charts']):
            with chart_cols[i % 2]:
                st.subheader(chart['title'])
                st.plotly_chart(chart['figure'], use_container_width=True)
    
    # Insights section
    if 'insights' in report['sections']:
        st.header("💡 Key Insights")
        insights = report['sections']['insights']
        
        for insight in insights['insights']:
            severity = insight['severity']
            icon = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❌'}.get(severity, 'ℹ️')
            
            if severity == 'warning':
                st.warning(f"{icon} **{insight['title']}**: {insight['description']}")
            elif severity == 'error':
                st.error(f"{icon} **{insight['title']}**: {insight['description']}")
            else:
                st.info(f"{icon} **{insight['title']}**: {insight['description']}")

else:
    # Default report interface
    st.header("📋 Report Generator")
    
    # Quick report options
    st.subheader("Quick Reports")
    
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    with quick_col1:
        if st.button("📊 Data Overview", use_container_width=True):
            # Generate quick data overview
            st.subheader("Data Overview")
            
            # Basic info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Missing Values", df.isnull().sum().sum())
            with col4:
                st.metric("Duplicates", df.duplicated().sum())
            
            # Column types
            st.subheader("Column Information")
            col_info = []
            for col in df.columns:
                col_info.append({
                    'Column': col,
                    'Type': str(df[col].dtype),
                    'Non-Null Count': df[col].count(),
                    'Unique Values': df[col].nunique(),
                    'Missing Values': df[col].isnull().sum()
                })
            
            st.dataframe(pd.DataFrame(col_info), use_container_width=True)
    
    with quick_col2:
        if st.button("📈 Statistical Summary", use_container_width=True):
            # Generate statistical summary
            st.subheader("Statistical Summary")
            
            # Numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                st.subheader("Numeric Columns")
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
            
            # Categorical columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                st.subheader("Categorical Columns")
                for col in categorical_cols:
                    with st.expander(f"📊 {col}"):
                        value_counts = df[col].value_counts().head(10)
                        fig = px.bar(
                            x=value_counts.index,
                            y=value_counts.values,
                            title=f"Top values in {col}"
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    with quick_col3:
        if st.button("🔍 Data Quality Check", use_container_width=True):
            # Generate data quality report
            st.subheader("Data Quality Report")
            
            # Missing values analysis
            missing_data = df.isnull().sum()
            missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
            
            if len(missing_data) > 0:
                st.subheader("Missing Values by Column")
                fig = px.bar(
                    x=missing_data.index,
                    y=missing_data.values,
                    title="Missing Values by Column"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No missing values found!")
            
            # Duplicate analysis
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                st.warning(f"⚠️ Found {duplicates} duplicate rows")
            else:
                st.success("✅ No duplicate rows found!")
            
            # Data type consistency
            st.subheader("Data Type Summary")
            dtype_counts = df.dtypes.value_counts()
            fig = px.pie(
                values=dtype_counts.values,
                names=dtype_counts.index,
                title="Data Types Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

# Custom report builder
st.markdown("---")
st.header("🛠️ Custom Report Builder")

custom_col1, custom_col2 = st.columns(2)

with custom_col1:
    st.subheader("Select Analysis Type")
    
    analysis_type = st.selectbox(
        "Choose analysis type",
        ["Descriptive Statistics", "Correlation Analysis", "Distribution Analysis", "Outlier Detection"]
    )
    
    if analysis_type == "Descriptive Statistics":
        selected_columns = st.multiselect(
            "Select columns for analysis",
            df.columns.tolist(),
            default=df.select_dtypes(include=['number']).columns.tolist()
        )
        
        if st.button("Generate Analysis"):
            if selected_columns:
                st.subheader("Descriptive Statistics")
                st.dataframe(df[selected_columns].describe(), use_container_width=True)
            else:
                st.warning("Please select at least one column")
    
    elif analysis_type == "Correlation Analysis":
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) > 1:
            if st.button("Generate Correlation Analysis"):
                st.subheader("Correlation Analysis")
                corr_matrix = df[numeric_cols].corr()
                
                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    title="Correlation Matrix",
                    color_continuous_scale="RdBu"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Need at least 2 numeric columns for correlation analysis")
    
    elif analysis_type == "Distribution Analysis":
        selected_column = st.selectbox(
            "Select column for distribution analysis",
            df.select_dtypes(include=['number']).columns.tolist()
        )
        
        if st.button("Generate Distribution Analysis"):
            if selected_column:
                st.subheader(f"Distribution of {selected_column}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.histogram(df, x=selected_column, title=f"Histogram of {selected_column}")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.box(df, y=selected_column, title=f"Box Plot of {selected_column}")
                    st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Outlier Detection":
        selected_column = st.selectbox(
            "Select column for outlier detection",
            df.select_dtypes(include=['number']).columns.tolist()
        )
        
        if st.button("Detect Outliers"):
            if selected_column:
                st.subheader(f"Outlier Detection for {selected_column}")
                
                # IQR method
                Q1 = df[selected_column].quantile(0.25)
                Q3 = df[selected_column].quantile(0.75)
                IQR = Q3 - Q1
                
                outliers = df[(df[selected_column] < Q1 - 1.5 * IQR) | 
                            (df[selected_column] > Q3 + 1.5 * IQR)]
                
                st.metric("Outliers Found", len(outliers))
                st.metric("Outlier Percentage", f"{len(outliers)/len(df)*100:.2f}%")
                
                if len(outliers) > 0:
                    st.subheader("Outlier Values")
                    st.dataframe(outliers[[selected_column]], use_container_width=True)

with custom_col2:
    st.subheader("Report Preview")
    st.info("Select an analysis type and click 'Generate Analysis' to see results here.")

# Mobile-responsive adjustments
st.markdown("""
<style>
@media (max-width: 768px) {
    .stColumn {
        width: 100% !important;
    }
    .stMetric {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)
