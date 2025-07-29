"""
Project overview search tool for real estate data.

This module provides functionality to search and query project overview information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class ProjectOverviewTools(BaseRealEstateTools):
    """Tools for searching project overview information."""
    
    def search_project_overview(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search project overview in the project_overview collection.
        
        Args:
            **criteria: Search criteria such as:
                - project_name: str (name of project)
                - status: str (project status)
                - developer: str (developer name)
                - segment: str (market segment)
                
        Returns:
            List of project overview data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['project_overview']]
            
            query = {}
            if 'project_name' in criteria:
                query['project_name'] = {'$regex': criteria['project_name'], '$options': 'i'}
            if 'status' in criteria:
                query['status'] = {'$regex': criteria['status'], '$options': 'i'}
            if 'developer' in criteria:
                query['developer'] = {'$regex': criteria['developer'], '$options': 'i'}
            if 'segment' in criteria:
                query['segment'] = {'$regex': criteria['segment'], '$options': 'i'}
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching project overview: {e}")
            return []
