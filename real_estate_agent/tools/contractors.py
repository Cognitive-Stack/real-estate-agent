"""
Contractors search tool for real estate data.

This module provides functionality to search and query contractor information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class ContractorsTools(BaseRealEstateTools):
    """Tools for searching contractor information."""
    
    def search_contractors(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search contractors in the contractors collection with flexible criteria.
        
        Args:
            **criteria: Search criteria such as:
                - name: str (contractor name - searches in contractor_name.value)
                - capacity: str (capacity/scale - searches in capacity_scale.value)
                - certificate: str (certificates - searches in professional_practice_certificate.value)
                - project: str (previous projects - searches in previous_completed_projects)
                - material: str (material quality - searches in material_quality.value)
                - technology: str (applied technology - searches in applied_technology.value)
                - philosophy: str (design philosophy - searches in design_philosophy.value)
                - general: str (general search across all text fields)
                
        Returns:
            List of contractor data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['contractors']]
            
            query = {}
            
            # Build specific field queries
            if 'name' in criteria:
                query['contractor_name.value'] = {'$regex': criteria['name'], '$options': 'i'}
            if 'capacity' in criteria:
                query['capacity_scale.value'] = {'$regex': criteria['capacity'], '$options': 'i'}
            if 'certificate' in criteria:
                query['professional_practice_certificate.value'] = {'$regex': criteria['certificate'], '$options': 'i'}
            if 'material' in criteria:
                query['material_quality.value'] = {'$regex': criteria['material'], '$options': 'i'}
            if 'technology' in criteria:
                query['applied_technology.value'] = {'$regex': criteria['technology'], '$options': 'i'}
            if 'philosophy' in criteria:
                query['design_philosophy.value'] = {'$regex': criteria['philosophy'], '$options': 'i'}
            
            # Project search (searches in array of previous projects)
            if 'project' in criteria:
                query['previous_completed_projects.value'] = {
                    '$elemMatch': {
                        'value': {'$regex': criteria['project'], '$options': 'i'}
                    }
                }
            
            # General search across all text fields
            if 'general' in criteria:
                search_term = criteria['general']
                query['$or'] = [
                    {'contractor_name.value': {'$regex': search_term, '$options': 'i'}},
                    {'capacity_scale.value': {'$regex': search_term, '$options': 'i'}},
                    {'professional_practice_certificate.value': {'$regex': search_term, '$options': 'i'}},
                    {'material_quality.value': {'$regex': search_term, '$options': 'i'}},
                    {'applied_technology.value': {'$regex': search_term, '$options': 'i'}},
                    {'design_philosophy.value': {'$regex': search_term, '$options': 'i'}},
                    {'previous_completed_projects.value': {
                        '$elemMatch': {
                            'value': {'$regex': search_term, '$options': 'i'}
                        }
                    }}
                ]
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching contractors: {e}")
            return []
