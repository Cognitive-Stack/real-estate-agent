"""
Living experience search tool for real estate data.

This module provides functionality to search and query living experience information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class LivingExperienceTools(BaseRealEstateTools):
    """Tools for searching living experience information."""
    
    def search_living_experience(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search living experience data in the living_experience collection.
        
        Args:
            **criteria: Search criteria such as:
                - amenity_type: str (type of amenity)
                - rating: int (experience rating)
                - category: str (experience category)
                
        Returns:
            List of living experience data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['living_experience']]
            
            query = {}
            if 'amenity_type' in criteria:
                query['amenity_type'] = {'$regex': criteria['amenity_type'], '$options': 'i'}
            if 'rating' in criteria:
                query['rating'] = criteria['rating']
            if 'category' in criteria:
                query['category'] = {'$regex': criteria['category'], '$options': 'i'}
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching living experience: {e}")
            return []
