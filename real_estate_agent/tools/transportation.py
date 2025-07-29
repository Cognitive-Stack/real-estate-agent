"""
Transportation search tool for real estate data.

This module provides functionality to search and query transportation information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class TransportationTools(BaseRealEstateTools):
    """Tools for searching transportation information."""
    
    def search_transportation(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search transportation data in the transportation collection.
        
        Args:
            **criteria: Search criteria such as:
                - transport_type: str (type of transportation)
                - distance: float (distance in km)
                - accessibility: str (accessibility level)
                
        Returns:
            List of transportation data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['transportation']]
            
            query = {}
            if 'transport_type' in criteria:
                query['transport_type'] = {'$regex': criteria['transport_type'], '$options': 'i'}
            if 'distance' in criteria:
                query['distance'] = {'$lte': criteria['distance']}
            if 'accessibility' in criteria:
                query['accessibility'] = {'$regex': criteria['accessibility'], '$options': 'i'}
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching transportation: {e}")
            return []
