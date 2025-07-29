"""
Legal status search tool for real estate data.

This module provides functionality to search and query legal status information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class LegalStatusTools(BaseRealEstateTools):
    """Tools for searching legal status information."""
    
    def search_legal_status(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search legal status in the legal_status collection.
        
        Args:
            **criteria: Search criteria such as:
                - status_type: str (type of legal status)
                - approval_date: str (approval date)
                - authority: str (approving authority)
                
        Returns:
            List of legal status data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['legal_status']]
            
            query = {}
            if 'status_type' in criteria:
                query['status_type'] = {'$regex': criteria['status_type'], '$options': 'i'}
            if 'approval_date' in criteria:
                query['approval_date'] = {'$regex': criteria['approval_date'], '$options': 'i'}
            if 'authority' in criteria:
                query['authority'] = {'$regex': criteria['authority'], '$options': 'i'}
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching legal status: {e}")
            return []
