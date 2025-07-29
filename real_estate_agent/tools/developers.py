"""
Developers search tool for real estate data.

This module provides functionality to search and query developer information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class DevelopersTools(BaseRealEstateTools):
    """Tools for searching developer information."""
    
    def search_developers(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search developers in the developers collection with flexible criteria.
        
        Args:
            **criteria: Search criteria such as:
                - name: str (developer name - searches in name.value)
                - year_founded: int (founding year - searches in year_founded.value)
                - min_year: int (minimum founding year)
                - max_year: int (maximum founding year)
                - financial_capacity: str (financial info - searches in financial_capacity.value)
                - project: str (completed projects - searches in completed_projects)
                - experience: str (searches in experience-related fields)
                - reputation: str (searches in reputation.value)
                - general: str (general search across all text fields)
                
        Returns:
            List of developer data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['developers']]
            
            query = {}
            
            # Build specific field queries
            if 'name' in criteria:
                query['name.value'] = {'$regex': criteria['name'], '$options': 'i'}
            if 'year_founded' in criteria:
                query['year_founded.value'] = criteria['year_founded']
            if 'min_year' in criteria:
                query['year_founded.value'] = {'$gte': criteria['min_year']}
            if 'max_year' in criteria:
                if 'year_founded.value' in query:
                    query['year_founded.value']['$lte'] = criteria['max_year']
                else:
                    query['year_founded.value'] = {'$lte': criteria['max_year']}
            if 'financial_capacity' in criteria:
                query['financial_capacity.value'] = {'$regex': criteria['financial_capacity'], '$options': 'i'}
            if 'experience' in criteria:
                query['experience.value'] = {'$regex': criteria['experience'], '$options': 'i'}
            if 'reputation' in criteria:
                query['reputation.value'] = {'$regex': criteria['reputation'], '$options': 'i'}
            
            # Project search (searches in array of completed projects)
            if 'project' in criteria:
                query['completed_projects.value'] = {
                    '$elemMatch': {
                        'value': {'$regex': criteria['project'], '$options': 'i'}
                    }
                }
            
            # General search across all text fields
            if 'general' in criteria:
                search_term = criteria['general']
                query['$or'] = [
                    {'name.value': {'$regex': search_term, '$options': 'i'}},
                    {'financial_capacity.value': {'$regex': search_term, '$options': 'i'}},
                    {'experience.value': {'$regex': search_term, '$options': 'i'}},
                    {'reputation.value': {'$regex': search_term, '$options': 'i'}},
                    {'completed_projects.value': {
                        '$elemMatch': {
                            'value': {'$regex': search_term, '$options': 'i'}
                        }
                    }}
                ]
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching developers: {e}")
            return []
