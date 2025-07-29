"""
Design layout search tool for real estate data.

This module provides functionality to search and query design layout information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class DesignLayoutTools(BaseRealEstateTools):
    """Tools for searching design layout information."""
    
    def search_design_layout(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search design layouts in the design_layout collection with flexible criteria.
        
        Args:
            **criteria: Search criteria such as:
                - bedrooms: int (exact number of bedrooms)
                - bathrooms: int (exact number of bathrooms)
                - toilet: int (exact number of toilets)
                - min_bedrooms: int (minimum number of bedrooms)
                - max_bedrooms: int (maximum number of bedrooms)
                - min_bathrooms: int (minimum number of bathrooms)
                - max_bathrooms: int (maximum number of bathrooms)
                - min_toilet: int (minimum number of toilets)
                - max_toilet: int (maximum number of toilets)
                - type: str (apartment type)
                - privacy: str (privacy features)
                - area: str (area description)
                - total_area: str (total area specification)
                - general: str (general search across all design fields)
                
        Returns:
            List of design layout data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['design_layout']]
            
            query = {}
            
            # Exact count searches
            for field in ['bedrooms', 'bathrooms', 'toilet']:
                if field in criteria:
                    query[f'{field}.value'] = criteria[field]
            
            # Range searches for room counts
            for field in ['bedrooms', 'bathrooms', 'toilet']:
                range_query = {}
                if f'min_{field}' in criteria:
                    range_query['$gte'] = criteria[f'min_{field}']
                if f'max_{field}' in criteria:
                    range_query['$lte'] = criteria[f'max_{field}']
                
                if range_query:
                    query[f'{field}.value'] = range_query
            
            # Text-based searches
            if 'type' in criteria:
                query['type.value'] = {'$regex': criteria['type'], '$options': 'i'}
            if 'privacy' in criteria:
                query['privacy.value'] = {
                    '$elemMatch': {
                        'value': {'$regex': criteria['privacy'], '$options': 'i'}
                    }
                }
            if 'area' in criteria:
                query['area.value'] = {'$regex': criteria['area'], '$options': 'i'}
            if 'total_area' in criteria:
                query['total_area.value'] = {'$regex': criteria['total_area'], '$options': 'i'}
            
            # General search across all fields
            if 'general' in criteria:
                search_term = criteria['general']
                general_query = {
                    '$or': [
                        {'type.value': {'$regex': search_term, '$options': 'i'}},
                        {'privacy.value': {
                            '$elemMatch': {
                                'value': {'$regex': search_term, '$options': 'i'}
                            }
                        }},
                        {'area.value': {'$regex': search_term, '$options': 'i'}},
                        {'total_area.value': {'$regex': search_term, '$options': 'i'}}
                    ]
                }
                if query:
                    query = {'$and': [query, general_query]}
                else:
                    query = general_query
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching design layouts: {e}")
            return []
