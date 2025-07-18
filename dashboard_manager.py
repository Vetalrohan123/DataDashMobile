import json
import os
import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime

class DashboardManager:
    """Manages dashboard configurations, saving, and loading."""
    
    def __init__(self):
        self.dashboards_dir = "dashboards"
        self.ensure_dashboards_directory()
    
    def ensure_dashboards_directory(self):
        """Ensure the dashboards directory exists."""
        if not os.path.exists(self.dashboards_dir):
            os.makedirs(self.dashboards_dir)
    
    def save_dashboard(self, dashboard_name: str, dashboard_config: Dict[str, Any]) -> bool:
        """Save a dashboard configuration."""
        try:
            # Add metadata
            dashboard_config['metadata'] = {
                'name': dashboard_name,
                'created_at': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            file_path = os.path.join(self.dashboards_dir, f"{dashboard_name}.json")
            with open(file_path, 'w') as f:
                json.dump(dashboard_config, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error saving dashboard: {str(e)}")
            return False
    
    def load_dashboard(self, dashboard_name: str) -> Optional[Dict[str, Any]]:
        """Load a dashboard configuration."""
        try:
            file_path = os.path.join(self.dashboards_dir, f"{dashboard_name}.json")
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                dashboard_config = json.load(f)
            
            return dashboard_config
        except Exception as e:
            st.error(f"Error loading dashboard: {str(e)}")
            return None
    
    def get_dashboard_list(self) -> List[str]:
        """Get list of saved dashboards."""
        try:
            dashboards = []
            for file in os.listdir(self.dashboards_dir):
                if file.endswith('.json'):
                    dashboards.append(file.replace('.json', ''))
            return sorted(dashboards)
        except Exception as e:
            st.error(f"Error getting dashboard list: {str(e)}")
            return []
    
    def delete_dashboard(self, dashboard_name: str) -> bool:
        """Delete a dashboard configuration."""
        try:
            file_path = os.path.join(self.dashboards_dir, f"{dashboard_name}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting dashboard: {str(e)}")
            return False
    
    def export_dashboard(self, dashboard_name: str) -> Optional[bytes]:
        """Export a dashboard configuration as JSON."""
        try:
            dashboard_config = self.load_dashboard(dashboard_name)
            if dashboard_config:
                return json.dumps(dashboard_config, indent=2).encode('utf-8')
            return None
        except Exception as e:
            st.error(f"Error exporting dashboard: {str(e)}")
            return None
    
    def import_dashboard(self, uploaded_file, dashboard_name: str) -> bool:
        """Import a dashboard configuration from JSON file."""
        try:
            dashboard_config = json.load(uploaded_file)
            
            # Validate the configuration
            if not self._validate_dashboard_config(dashboard_config):
                st.error("Invalid dashboard configuration")
                return False
            
            # Update metadata
            if 'metadata' in dashboard_config:
                dashboard_config['metadata']['name'] = dashboard_name
                dashboard_config['metadata']['last_modified'] = datetime.now().isoformat()
            
            return self.save_dashboard(dashboard_name, dashboard_config)
        except Exception as e:
            st.error(f"Error importing dashboard: {str(e)}")
            return False
    
    def _validate_dashboard_config(self, config: Dict[str, Any]) -> bool:
        """Validate dashboard configuration structure."""
        required_fields = ['layout', 'charts']
        
        for field in required_fields:
            if field not in config:
                return False
        
        # Validate charts structure
        if not isinstance(config['charts'], list):
            return False
        
        for chart in config['charts']:
            if not isinstance(chart, dict):
                return False
            if 'id' not in chart or 'type' not in chart or 'config' not in chart:
                return False
        
        return True
    
    def create_default_dashboard(self) -> Dict[str, Any]:
        """Create a default dashboard configuration."""
        return {
            'layout': {
                'type': 'grid',
                'rows': 3,
                'cols': 2,
                'gap': 10
            },
            'charts': [],
            'filters': {},
            'metadata': {
                'name': 'New Dashboard',
                'created_at': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
    
    def duplicate_dashboard(self, source_name: str, target_name: str) -> bool:
        """Duplicate an existing dashboard."""
        try:
            source_config = self.load_dashboard(source_name)
            if not source_config:
                return False
            
            # Update metadata for the duplicate
            source_config['metadata']['name'] = target_name
            source_config['metadata']['created_at'] = datetime.now().isoformat()
            source_config['metadata']['last_modified'] = datetime.now().isoformat()
            
            return self.save_dashboard(target_name, source_config)
        except Exception as e:
            st.error(f"Error duplicating dashboard: {str(e)}")
            return False
    
    def get_dashboard_info(self, dashboard_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a dashboard."""
        try:
            dashboard_config = self.load_dashboard(dashboard_name)
            if not dashboard_config:
                return None
            
            return {
                'name': dashboard_name,
                'metadata': dashboard_config.get('metadata', {}),
                'chart_count': len(dashboard_config.get('charts', [])),
                'has_filters': bool(dashboard_config.get('filters', {}))
            }
        except Exception as e:
            st.error(f"Error getting dashboard info: {str(e)}")
            return None
    
    def update_dashboard_metadata(self, dashboard_name: str, metadata: Dict[str, Any]) -> bool:
        """Update dashboard metadata."""
        try:
            dashboard_config = self.load_dashboard(dashboard_name)
            if not dashboard_config:
                return False
            
            dashboard_config['metadata'].update(metadata)
            dashboard_config['metadata']['last_modified'] = datetime.now().isoformat()
            
            return self.save_dashboard(dashboard_name, dashboard_config)
        except Exception as e:
            st.error(f"Error updating dashboard metadata: {str(e)}")
            return False
