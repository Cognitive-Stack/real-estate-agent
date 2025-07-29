"""
Legal information search tool for real estate data.

This module provides functionality to search and query legal information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class LegalInfoTools(BaseRealEstateTools):
    """Tools for searching legal information."""
    
    def search_legal_info(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search legal information in the legal_info collection.
        
        Args:
            **criteria: Search criteria such as:
                - document_type: str (type of legal document)
                - status: str (legal status)
                - jurisdiction: str (legal jurisdiction)
                
        Returns:
            List of legal information data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['legal_info']]
            
            query = {}
            if 'document_type' in criteria:
                query['document_type'] = {'$regex': criteria['document_type'], '$options': 'i'}
            if 'status' in criteria:
                query['status'] = {'$regex': criteria['status'], '$options': 'i'}
            if 'jurisdiction' in criteria:
                query['jurisdiction'] = {'$regex': criteria['jurisdiction'], '$options': 'i'}
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching legal info: {e}")
            return []
