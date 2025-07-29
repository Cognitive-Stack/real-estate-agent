"""
Investment information search tool for real estate data.

This module provides functionality to search and query investment information.
"""

from typing import List, Dict, Any
from .base import BaseRealEstateTools


class InvestmentInfoTools(BaseRealEstateTools):
    """Tools for searching investment information."""
    
    def search_investment_info(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search investment information in the investment_info collection.
        
        Args:
            **criteria: Search criteria such as:
                - investment_type: str (type of investment)
                - min_amount: float (minimum investment amount)
                - max_amount: float (maximum investment amount)
                - roi: str (return on investment)
                
        Returns:
            List of investment data matching the criteria
        """
        try:
            self._ensure_connection()
            collection = self.db[self.collections['investment_info']]
            
            query = {}
            if 'investment_type' in criteria:
                query['investment_type'] = {'$regex': criteria['investment_type'], '$options': 'i'}
            if 'min_amount' in criteria:
                query['amount'] = {'$gte': criteria['min_amount']}
            if 'max_amount' in criteria:
                if 'amount' in query:
                    query['amount']['$lte'] = criteria['max_amount']
                else:
                    query['amount'] = {'$lte': criteria['max_amount']}
            if 'roi' in criteria:
                query['roi'] = {'$regex': criteria['roi'], '$options': 'i'}
            
            return list(collection.find(query))
        except Exception as e:
            print(f"Error searching investment info: {e}")
            return []
