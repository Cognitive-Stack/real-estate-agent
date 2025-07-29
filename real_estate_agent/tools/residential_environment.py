"""
Residential environment search tool for real estate data.

This module provides functionality to search and query residential environment information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class ResidentialEnvironmentTools(BaseRealEstateTools):
    """Tools for searching residential environment information."""
    
    def search_residential_environment(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search residential environment data in the residential_environment collection.
        
        Args:
            **criteria: Search criteria such as:
                - environment_type: str (type of environment)
                - quality_rating: int (quality rating)
                - features: str (environmental features)
                
        Returns:
            List of residential environment data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['residential_environment']]
            
            query = {}
            if 'environment_type' in criteria:
                query['environment_type'] = {'$regex': criteria['environment_type'], '$options': 'i'}
            if 'quality_rating' in criteria:
                query['quality_rating'] = criteria['quality_rating']
            if 'features' in criteria:
                query['features'] = {'$regex': criteria['features'], '$options': 'i'}
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching residential environment: {e}")
            return []
