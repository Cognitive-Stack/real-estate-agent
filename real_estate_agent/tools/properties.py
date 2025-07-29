"""
Properties search tool for real estate data.

This module provides functionality to search and query property information
across multiple MongoDB collections including properties, physical features,
design layout, legal status, locations, and project overview.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class PropertiesTools(BaseRealEstateTools):
    """Tools for searching property information."""
    
    def search_properties(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search properties across multiple collections using aggregation pipeline.
        
        Args:
            **criteria: Search criteria such as:
                - unit_id: str (specific unit identifier)
                - group_ids: list (project group identifiers)
                - description: str (property description text search)
                - bedrooms: int (number of bedrooms)
                - bathrooms: int (number of bathrooms)
                - floor_area_range: tuple (min_area, max_area) for gross_floor_area
                - apartment_floor: int (specific floor number)
                - unit_type: str (unit type from design_layout)
                - price_range: tuple (min_price, max_price) for total_price
                - price_per_sqm_range: tuple (min_price_sqm, max_price_sqm)
                - construction_status: str (legal status)
                - inventory_status: str (availability status)
                - project_name: str (from project_overview)
                - selling_price_range: tuple (min_price, max_price) for project selling price
                - rental_price_range: tuple (min_price, max_price) for project rental price
                - project_status: str (project status)
                - exact_location: str (location search)
                
        Returns:
            List of aggregated property data matching the criteria
        """
        try:
            self._ensure_connection()
            
            # Start with properties collection as base
            properties_collection = self.db[self.collections['properties']]
            
            # Build match criteria for properties collection
            properties_match = {}
            if 'unit_id' in criteria:
                properties_match['unit_id'] = criteria['unit_id']
            if 'group_ids' in criteria:
                properties_match['group_ids'] = {'$in': criteria['group_ids']}
            if 'description' in criteria:
                properties_match['description'] = {'$regex': criteria['description'], '$options': 'i'}
            
            # Aggregation pipeline to join with related collections
            pipeline = []
            
            # Match properties first
            if properties_match:
                pipeline.append({'$match': properties_match})
            
            # Join with physical_features
            pipeline.append({
                '$lookup': {
                    'from': self.collections['physical_features'],
                    'localField': 'unit_id',
                    'foreignField': 'unit_id',
                    'as': 'physical_features'
                }
            })
            
            # Join with design_layout
            pipeline.append({
                '$lookup': {
                    'from': self.collections['design_layout'],
                    'localField': 'unit_id',
                    'foreignField': 'unit_id',
                    'as': 'design_layout'
                }
            })
            
            # Join with legal_status
            pipeline.append({
                '$lookup': {
                    'from': self.collections['legal_status'],
                    'localField': 'unit_id',
                    'foreignField': 'unit_id',
                    'as': 'legal_status'
                }
            })
            
            # Join with locations using group_ids
            pipeline.append({
                '$lookup': {
                    'from': self.collections['locations'],
                    'localField': 'group_ids',
                    'foreignField': 'group_id',
                    'as': 'locations'
                }
            })
            
            # Join with project_overview using group_ids
            pipeline.append({
                '$lookup': {
                    'from': self.collections['project_overview'],
                    'localField': 'group_ids',
                    'foreignField': 'group_id',
                    'as': 'project_overview'
                }
            })
            
            # Build match criteria for joined collections
            match_criteria = {}
            
            # Physical features criteria
            if 'bedrooms' in criteria:
                match_criteria['physical_features.number_of_bedrooms'] = criteria['bedrooms']
            if 'bathrooms' in criteria:
                match_criteria['physical_features.number_of_bathrooms'] = criteria['bathrooms']
            if 'floor_area_range' in criteria and isinstance(criteria['floor_area_range'], tuple) and len(criteria['floor_area_range']) == 2:
                min_area, max_area = criteria['floor_area_range']
                match_criteria['physical_features.gross_floor_area'] = {'$gte': min_area, '$lte': max_area}
            if 'apartment_floor' in criteria:
                match_criteria['physical_features.apartment_floor'] = criteria['apartment_floor']
            
            # Design layout criteria
            if 'unit_type' in criteria:
                match_criteria['design_layout.unit_type'] = {'$regex': criteria['unit_type'], '$options': 'i'}
            
            # Legal status criteria
            if 'price_range' in criteria and isinstance(criteria['price_range'], tuple) and len(criteria['price_range']) == 2:
                min_price, max_price = criteria['price_range']
                match_criteria['legal_status.total_price'] = {'$gte': min_price, '$lte': max_price}
            if 'price_per_sqm_range' in criteria and isinstance(criteria['price_per_sqm_range'], tuple) and len(criteria['price_per_sqm_range']) == 2:
                min_price_sqm, max_price_sqm = criteria['price_per_sqm_range']
                match_criteria['legal_status.price_per_sqm'] = {'$gte': min_price_sqm, '$lte': max_price_sqm}
            if 'construction_status' in criteria:
                match_criteria['legal_status.construction_status'] = {'$regex': criteria['construction_status'], '$options': 'i'}
            if 'inventory_status' in criteria:
                match_criteria['legal_status.inventory_status'] = {'$regex': criteria['inventory_status'], '$options': 'i'}
            
            # Location criteria
            if 'exact_location' in criteria:
                match_criteria['locations.exact_location_on_map'] = {'$regex': criteria['exact_location'], '$options': 'i'}
            
            # Project overview criteria
            if 'project_name' in criteria:
                match_criteria['project_overview.project_name'] = {'$regex': criteria['project_name'], '$options': 'i'}
            if 'selling_price_range' in criteria and isinstance(criteria['selling_price_range'], tuple) and len(criteria['selling_price_range']) == 2:
                min_price, max_price = criteria['selling_price_range']
                match_criteria['project_overview.selling_price'] = {'$gte': min_price, '$lte': max_price}
            if 'rental_price_range' in criteria and isinstance(criteria['rental_price_range'], tuple) and len(criteria['rental_price_range']) == 2:
                min_price, max_price = criteria['rental_price_range']
                match_criteria['project_overview.rental_price'] = {'$gte': min_price, '$lte': max_price}
            if 'project_status' in criteria:
                match_criteria['project_overview.status'] = {'$regex': criteria['project_status'], '$options': 'i'}
            
            # Apply match criteria for joined collections
            if match_criteria:
                pipeline.append({'$match': match_criteria})
            
            # Execute aggregation
            results = list(properties_collection.aggregate(pipeline))
            return results
            
        except Exception as e:
            print(f"Error searching properties: {e}")
            return []
    
    def search_properties_simple(self, 
                                bedrooms=None, 
                                bathrooms=None,
                                price_range=None,
                                unit_type=None,
                                project_name=None,
                                location=None) -> List[Dict[str, Any]]:
        """
        Simplified property search with common criteria.
        
        Args:
            bedrooms: int (number of bedrooms)
            bathrooms: int (number of bathrooms)
            price_range: tuple (min_price, max_price) for total_price
            unit_type: str (unit type)
            project_name: str (project name)
            location: str (location search)
            
        Returns:
            List of property data matching the criteria
        """
        criteria = {}
        if bedrooms is not None:
            criteria['bedrooms'] = bedrooms
        if bathrooms is not None:
            criteria['bathrooms'] = bathrooms
        if price_range is not None:
            criteria['price_range'] = price_range
        if unit_type is not None:
            criteria['unit_type'] = unit_type
        if project_name is not None:
            criteria['project_name'] = project_name
        if location is not None:
            criteria['exact_location'] = location
            
        return self.search_properties(**criteria)