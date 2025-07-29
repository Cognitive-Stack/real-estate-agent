"""
Locations search tool for real estate data.

This module provides functionality to search and query location information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class LocationsTools(BaseRealEstateTools):
    """Tools for searching location information."""
    
    def search_locations(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search locations in the locations collection with flexible criteria.
        
        Args:
            **criteria: Search criteria such as:
                - longitude: float (exact longitude)
                - latitude: float (exact latitude)
                - min_longitude: float (minimum longitude for range search)
                - max_longitude: float (maximum longitude for range search)
                - min_latitude: float (minimum latitude for range search)
                - max_latitude: float (maximum latitude for range search)
                - planning: str (searches in planning information)
                - connectivity: str (searches in connectivity information)
                - amenities: str (searches in surrounding amenities)
                - general: str (general search across all location fields)
                
        Returns:
            List of location data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['locations']]
            
            query = {}
            
            # Coordinate-based searches
            if 'longitude' in criteria:
                query['exact_location_on_map.value'] = {
                    '$elemMatch': {
                        'key': 'longitude',
                        'value': criteria['longitude']
                    }
                }
            if 'latitude' in criteria:
                if 'exact_location_on_map.value' not in query:
                    query['exact_location_on_map.value'] = {'$elemMatch': {}}
                # For multiple coordinates, we need separate queries or use $and
                lat_query = {
                    'exact_location_on_map.value': {
                        '$elemMatch': {
                            'key': 'latitude',
                            'value': criteria['latitude']
                        }
                    }
                }
                if 'exact_location_on_map.value' in query:
                    # Combine with existing longitude query using $and
                    existing_query = query.copy()
                    query = {'$and': [existing_query, lat_query]}
                else:
                    query.update(lat_query)
            
            # Range-based coordinate searches
            coordinate_ranges = {}
            if 'min_longitude' in criteria or 'max_longitude' in criteria:
                coord_query = {}
                if 'min_longitude' in criteria:
                    coord_query['$gte'] = criteria['min_longitude']
                if 'max_longitude' in criteria:
                    coord_query['$lte'] = criteria['max_longitude']
                coordinate_ranges['longitude'] = coord_query
            
            if 'min_latitude' in criteria or 'max_latitude' in criteria:
                coord_query = {}
                if 'min_latitude' in criteria:
                    coord_query['$gte'] = criteria['min_latitude']
                if 'max_latitude' in criteria:
                    coord_query['$lte'] = criteria['max_latitude']
                coordinate_ranges['latitude'] = coord_query
            
            # Apply coordinate range queries
            for coord_type, range_query in coordinate_ranges.items():
                range_condition = {
                    'exact_location_on_map.value': {
                        '$elemMatch': {
                            'key': coord_type,
                            'value': range_query
                        }
                    }
                }
                if '$and' not in query:
                    if query:
                        query = {'$and': [query, range_condition]}
                    else:
                        query = range_condition
                else:
                    query['$and'].append(range_condition)
            
            # Text-based searches
            if 'planning' in criteria:
                query['planning.value'] = {
                    '$elemMatch': {
                        'value': {'$regex': criteria['planning'], '$options': 'i'}
                    }
                }
            if 'connectivity' in criteria:
                query['connectivity.value'] = {'$regex': criteria['connectivity'], '$options': 'i'}
            if 'amenities' in criteria:
                query['surrounding_amenities.value'] = {
                    '$elemMatch': {
                        'value': {'$regex': criteria['amenities'], '$options': 'i'}
                    }
                }
            
            # General search across all text fields
            if 'general' in criteria:
                search_term = criteria['general']
                general_query = {
                    '$or': [
                        {'planning.value': {
                            '$elemMatch': {
                                'value': {'$regex': search_term, '$options': 'i'}
                            }
                        }},
                        {'connectivity.value': {'$regex': search_term, '$options': 'i'}},
                        {'surrounding_amenities.value': {
                            '$elemMatch': {
                                'value': {'$regex': search_term, '$options': 'i'}
                            }
                        }}
                    ]
                }
                if query:
                    query = {'$and': [query, general_query]}
                else:
                    query = general_query
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching locations: {e}")
            return []
