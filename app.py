import streamlit as st
import pandas as pd
import json
import os
from utils.data_handler import DataHandler
from utils.dashboard_manager import DashboardManager

# Configure the page
st.set_page_config(
    page_title="Analytics Dashboard Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

if 'dashboard_manager' not in st.session_state:
    st.session_state.dashboard_manager = DashboardManager()

if 'current_data' not in st.session_state:
    st.session_state.current_data = None

if 'dashboards' not in st.session_state:
    st.session_state.dashboards = {}

if 'current_dashboard' not in st.session_state:
    st.session_state.current_dashboard = None

# Main page content
st.title("📊 Analytics Dashboard Tool")
st.markdown("### Build custom dashboards and reports with ease")

# Mobile-friendly layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    #### Welcome to your analytics workspace!
    
    This tool helps you create interactive dashboards and reports from your data.
    
    **Features:**
    - 📁 Upload CSV and Excel files
    - 🎨 Drag-and-drop dashboard builder
    - 📊 Multiple chart types (bar, line, pie, scatter)
    - 🔍 Advanced filtering and data manipulation
    - 📱 Mobile-friendly interface
    - 💾 Save and load dashboard configurations
    - 📤 Export dashboards and reports
    """)

# Data upload section
st.markdown("---")
st.subheader("📁 Data Upload")

uploaded_file = st.file_uploader(
    "Upload your data file",
    type=['csv', 'xlsx', 'xls'],
    help="Supported formats: CSV, Excel (.xlsx, .xls)"
)

if uploaded_file is not None:
    try:
        # Process the uploaded file
        data = st.session_state.data_handler.load_data(uploaded_file)
        st.session_state.current_data = data
        
        st.success(f"✅ Data loaded successfully! Shape: {data.shape}")
        
        # Display data preview
        st.markdown("#### Data Preview")
        st.dataframe(data.head(10), use_container_width=True)
        
        # Display basic statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Rows", data.shape[0])
        with col2:
            st.metric("Columns", data.shape[1])
        with col3:
            st.metric("Numeric Columns", len(data.select_dtypes(include=['number']).columns))
        with col4:
            st.metric("Text Columns", len(data.select_dtypes(include=['object']).columns))
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")

# Quick actions
if st.session_state.current_data is not None:
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Create Dashboard", use_container_width=True):
            st.switch_page("pages/1_📊_Dashboard_Builder.py")
    
    with col2:
        if st.button("📈 Generate Report", use_container_width=True):
            st.switch_page("pages/2_📈_Reports.py")
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.switch_page("pages/3_⚙️_Settings.py")

# Sidebar navigation
with st.sidebar:
    st.markdown("### Navigation")
    st.markdown("Use the pages above to navigate through the application")
    
    if st.session_state.current_data is not None:
        st.markdown("---")
        st.markdown("### Current Dataset")
        st.info(f"📊 {st.session_state.current_data.shape[0]} rows × {st.session_state.current_data.shape[1]} columns")
        
        # Show column types
        st.markdown("#### Column Types")
        numeric_cols = st.session_state.current_data.select_dtypes(include=['number']).columns
        text_cols = st.session_state.current_data.select_dtypes(include=['object']).columns
        
        if len(numeric_cols) > 0:
            st.markdown("**Numeric:**")
            for col in numeric_cols:
                st.markdown(f"• {col}")
        
        if len(text_cols) > 0:
            st.markdown("**Text:**")
            for col in text_cols:
                st.markdown(f"• {col}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
    📱 Mobile-friendly • 🔒 Secure • 🚀 Fast
    </div>
    """,
    unsafe_allow_html=True
)
