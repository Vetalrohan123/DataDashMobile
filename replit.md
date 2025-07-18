# Analytics Dashboard Tool

## Overview

This is a Streamlit-based analytics dashboard application that provides users with tools to upload data, create interactive dashboards, generate reports, and manage their analytics workspace. The application follows a modular architecture with separate utility modules for different functionalities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for its simplicity in creating data applications with Python
- **Layout**: Multi-page application with a main app.py entry point and separate pages for different functionalities
- **UI Components**: Plotly for interactive charts and visualizations
- **State Management**: Streamlit's session state for maintaining user data and dashboard configurations across page navigation

### Backend Architecture
- **Language**: Python
- **Structure**: Modular utility classes handling specific functionalities
- **Data Processing**: Pandas for data manipulation and analysis
- **Visualization**: Plotly Express and Plotly Graph Objects for creating interactive charts

## Key Components

### Core Pages
1. **Main Application (app.py)**: Entry point and home page with welcome interface
2. **Dashboard Builder (pages/1_📊_Dashboard_Builder.py)**: Interactive dashboard creation interface
3. **Reports (pages/2_📈_Reports.py)**: Report generation and analytics interface
4. **Settings (pages/3_⚙️_Settings.py)**: Configuration and data management interface

### Utility Modules
1. **DataHandler (utils/data_handler.py)**: Manages data loading from CSV/Excel files, data processing, and column analysis
2. **ChartBuilder (utils/chart_builder.py)**: Creates various chart types (bar, line, pie, scatter, histogram, box, heatmap, area) using Plotly
3. **DashboardManager (utils/dashboard_manager.py)**: Handles dashboard configuration saving/loading to JSON files
4. **ReportGenerator (utils/report_generator.py)**: Generates comprehensive reports with multiple sections

## Data Flow

1. **Data Upload**: Users upload CSV or Excel files through the main interface
2. **Data Processing**: DataHandler processes and analyzes the uploaded data
3. **Dashboard Creation**: Users create charts using ChartBuilder and arrange them using DashboardManager
4. **Report Generation**: ReportGenerator creates comprehensive reports with statistics and insights
5. **Persistence**: Dashboard configurations are saved as JSON files in a local directory

## External Dependencies

### Required Python Packages
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualization library
- **numpy**: Numerical computing support
- **openpyxl**: Excel file reading (implied by xlsx support)

### File System Dependencies
- **dashboards/**: Directory for storing dashboard configurations as JSON files
- **Supported file formats**: CSV, XLSX, XLS for data upload

## Deployment Strategy

### Local Development
- Standard Streamlit application that can be run with `streamlit run app.py`
- File-based persistence for dashboard configurations
- No external database dependencies

### Production Considerations
- The application uses local file system for dashboard storage
- No authentication or user management system implemented
- Suitable for single-user or trusted environment deployment
- Could be enhanced with database integration for multi-user scenarios

### Scalability Notes
- Current architecture is designed for single-user desktop application usage
- Dashboard storage uses local JSON files which may not scale for multiple users
- Data processing is done in-memory which may limit dataset size capabilities
- No caching mechanism implemented for large datasets

### Mobile Responsiveness
- Application includes mobile-friendly layout considerations
- Uses Streamlit's column layout system for responsive design
- Wide layout configuration for better dashboard viewing experience