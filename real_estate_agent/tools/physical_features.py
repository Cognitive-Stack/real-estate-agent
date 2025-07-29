"""
Physical features search tool for real estate data.

This module provides functionality to search and query physical features information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class PhysicalFeaturesTools(BaseRealEstateTools):
    """Tools for searching physical features information."""
    
    def search_physical_features(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search physical features in the physical_features collection.
        
        Args:
            **criteria: Search criteria such as:
                - feature_type: str (type of physical feature)
                - value: str (feature value)
                - unit: str (measurement unit)
                
        Returns:
            List of physical feature data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['physical_features']]
            
            query = {}
            if 'feature_type' in criteria:
                query['feature_type'] = {'$regex': criteria['feature_type'], '$options': 'i'}
            if 'value' in criteria:
                query['value'] = criteria['value']
            if 'unit' in criteria:
                query['unit'] = {'$regex': criteria['unit'], '$options': 'i'}
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching physical features: {e}")
            return []
