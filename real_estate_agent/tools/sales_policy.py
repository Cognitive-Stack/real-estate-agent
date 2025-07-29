"""
Sales policy search tool for real estate data.

This module provides functionality to search and query sales policy information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class SalesPolicyTools(BaseRealEstateTools):
    """Tools for searching sales policy information."""
    
    def search_sales_policy(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search sales policy in the sales_policy collection.
        
        Args:
            **criteria: Search criteria such as:
                - policy_type: str (type of sales policy)
                - discount_rate: float (discount percentage)
                - payment_terms: str (payment terms)
                
        Returns:
            List of sales policy data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['sales_policy']]
            
            query = {}
            if 'policy_type' in criteria:
                query['policy_type'] = {'$regex': criteria['policy_type'], '$options': 'i'}
            if 'discount_rate' in criteria:
                query['discount_rate'] = criteria['discount_rate']
            if 'payment_terms' in criteria:
                query['payment_terms'] = {'$regex': criteria['payment_terms'], '$options': 'i'}
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching sales policy: {e}")
            return []
