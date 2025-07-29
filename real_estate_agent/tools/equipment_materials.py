"""
Equipment and materials search tool for real estate data.

This module provides functionality to search and query equipment and materials information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class EquipmentMaterialsTools(BaseRealEstateTools):
    """Tools for searching equipment and materials information."""
    
    def search_equipment_materials(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search equipment and materials in the equipment_materials collection with flexible criteria.
        
        Args:
            **criteria: Search criteria such as:
                - sanitary_equipment: str (sanitary equipment brand/type)
                - kitchen_equipment: str (kitchen equipment brand/type)
                - electrical_equipment: str (electrical equipment brand/type)
                - interior_materials: str (interior materials type/brand)
                - exterior_materials: str (exterior materials type/brand)
                - brand: str (any equipment or material brand)
                - type: str (equipment or material type)
                - general: str (general search across all equipment and material fields)
                
        Returns:
            List of equipment and materials data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['equipment_materials']]
            
            query = {}
            
            # Specific equipment category searches
            equipment_fields = [
                'sanitary_equipment', 'kitchen_equipment', 'electrical_equipment',
                'interior_materials', 'exterior_materials'
            ]
            
            for field in equipment_fields:
                if field in criteria:
                    query[f'{field}.value'] = {
                        '$elemMatch': {
                            'value': {'$regex': criteria[field], '$options': 'i'}
                        }
                    }
            
            # Brand search across all equipment categories
            if 'brand' in criteria:
                brand_conditions = []
                for field in equipment_fields:
                    brand_conditions.append({
                        f'{field}.value': {
                            '$elemMatch': {
                                'value': {'$regex': criteria['brand'], '$options': 'i'}
                            }
                        }
                    })
                
                brand_query = {'$or': brand_conditions}
                if query:
                    query = {'$and': [query, brand_query]}
                else:
                    query = brand_query
            
            # Type search across all equipment categories
            if 'type' in criteria:
                type_conditions = []
                for field in equipment_fields:
                    type_conditions.append({
                        f'{field}.value': {
                            '$elemMatch': {
                                'value': {'$regex': criteria['type'], '$options': 'i'}
                            }
                        }
                    })
                
                type_query = {'$or': type_conditions}
                if query:
                    query = {'$and': [query, type_query]}
                else:
                    query = type_query
            
            # General search across all equipment and material fields
            if 'general' in criteria:
                search_term = criteria['general']
                general_conditions = []
                for field in equipment_fields:
                    general_conditions.append({
                        f'{field}.value': {
                            '$elemMatch': {
                                'value': {'$regex': search_term, '$options': 'i'}
                            }
                        }
                    })
                
                general_query = {'$or': general_conditions}
                if query:
                    query = {'$and': [query, general_query]}
                else:
                    query = general_query
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching equipment and materials: {e}")
            return []
