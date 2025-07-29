"""
Real Estate Data Query Tools

This module provides tools for the real estate agent to query and analyze
property data and property group data from mock data sources.
"""

import json
import os
from typing import List, Dict, Any, Optional, Union, Annotated
from pathlib import Path
from datetime import datetime


from datetime import datetime


class UserPreferenceManager:
    """Manager for user preferences with JSON file storage."""
    
    def __init__(self, preferences_file: str = None):
        """
        Initialize the preference manager.
        
        Args:
            preferences_file: Path to the preferences JSON file. If None, uses default path.
        """
        if preferences_file is None:
            # Get the project root directory and store preferences there
            current_dir = Path(__file__).parent.parent
            self.preferences_file = current_dir / "user_preferences.json"
        else:
            self.preferences_file = Path(preferences_file)
        
        # Ensure the directory exists
        self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create initial preferences
        self._load_or_create_preferences()
    
    def _load_or_create_preferences(self):
        """Load existing preferences or create a new file with default structure."""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    self.preferences = json.load(f)
            else:
                # Create default preferences structure
                self.preferences = {
                    "user_profile": {
                        "name": "",
                        "phone_number": "",
                        "email": "",
                        "age": None,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    },
                    "property_preferences": {
                        "property_type": [],  # e.g., ["apartment", "condo", "house"]
                        "budget_min": None,
                        "budget_max": None,
                        "currency": "VND",
                        "locations": [],  # preferred locations
                        "bedrooms_min": None,
                        "bedrooms_max": None,
                        "bathrooms_min": None,
                        "size_min_sqm": None,
                        "size_max_sqm": None,
                        "must_have_amenities": [],  # required amenities
                        "nice_to_have_amenities": [],  # preferred but not required
                        "updated_at": datetime.now().isoformat()
                    },
                    "search_history": [],
                    "conversation_context": {
                        "last_search_criteria": {},
                        "recent_interests": [],
                        "updated_at": datetime.now().isoformat()
                    }
                }
                self._save_preferences()
        except Exception as e:
            print(f"Error loading preferences: {e}")
            self.preferences = {}
    
    def _save_preferences(self):
        """Save preferences to JSON file."""
        try:
            # Update the last modified timestamp
            self.preferences["user_profile"]["updated_at"] = datetime.now().isoformat()
            
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def update_user_profile(self, **kwargs):
        """Update user profile information."""
        for key, value in kwargs.items():
            if key in self.preferences["user_profile"]:
                self.preferences["user_profile"][key] = value
        self._save_preferences()
    
    def update_property_preferences(self, **kwargs):
        """Update property preferences."""
        for key, value in kwargs.items():
            if key in self.preferences["property_preferences"]:
                self.preferences["property_preferences"][key] = value
        self.preferences["property_preferences"]["updated_at"] = datetime.now().isoformat()
        self._save_preferences()
    
    def add_to_search_history(self, search_criteria: Dict[str, Any]):
        """Add a search to the history."""
        search_entry = {
            "criteria": search_criteria,
            "timestamp": datetime.now().isoformat()
        }
        self.preferences["search_history"].append(search_entry)
        
        # Keep only the last 50 searches
        if len(self.preferences["search_history"]) > 50:
            self.preferences["search_history"] = self.preferences["search_history"][-50:]
        
        self._save_preferences()
    
    def update_conversation_context(self, **kwargs):
        """Update conversation context."""
        for key, value in kwargs.items():
            if key in self.preferences["conversation_context"]:
                self.preferences["conversation_context"][key] = value
        self.preferences["conversation_context"]["updated_at"] = datetime.now().isoformat()
        self._save_preferences()
    
    def get_preferences(self):
        """Get all preferences."""
        return self.preferences.copy()
    
    def get_user_profile(self):
        """Get user profile."""
        return self.preferences.get("user_profile", {}).copy()
    
    def get_property_preferences(self):
        """Get property preferences."""
        return self.preferences.get("property_preferences", {}).copy()


class RealEstateDataTools:
    """Tools for querying real estate property and project data."""
    
    def __init__(self, mock_data_dir: str = None):
        """
        Initialize the data tools.
        
        Args:
            mock_data_dir: Path to the mock data directory. If None, uses default path.
        """
        if mock_data_dir is None:
            # Get the directory of the current file and navigate to mock_data
            current_dir = Path(__file__).parent
            self.mock_data_dir = current_dir.parent / "mock_data"
        else:
            self.mock_data_dir = Path(mock_data_dir)
        
        self.properties_file = self.mock_data_dir / "mock_property_schema_data.json"
        self.property_groups_file = self.mock_data_dir / "mock_property_group_schema_data.json"
        
        # Load data on initialization
        self._properties_data = None
        self._property_groups_data = None
        self._load_data()
    
    def _load_data(self):
        """Load data from JSON files."""
        try:
            if self.properties_file.exists():
                with open(self.properties_file, 'r', encoding='utf-8') as f:
                    self._properties_data = json.load(f)
            else:
                print(f"Warning: Properties file not found at {self.properties_file}")
                self._properties_data = []
            
            if self.property_groups_file.exists():
                with open(self.property_groups_file, 'r', encoding='utf-8') as f:
                    self._property_groups_data = json.load(f)
            else:
                print(f"Warning: Property groups file not found at {self.property_groups_file}")
                self._property_groups_data = []
                
        except Exception as e:
            print(f"Error loading data: {e}")
            self._properties_data = []
            self._property_groups_data = []
    
    def get_all_properties(self) -> List[Dict[str, Any]]:
        """
        Get all properties from the dataset.
        
        Returns:
            List of all property data dictionaries
        """
        return self._properties_data or []
    
    def get_all_property_groups(self) -> List[Dict[str, Any]]:
        """
        Get all property groups from the dataset.
        
        Returns:
            List of all property group data dictionaries
        """
        return self._property_groups_data or []
    
    def get_property_by_id(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific property by its unit ID.
        
        Args:
            unit_id: The unit ID to search for
            
        Returns:
            Property data dictionary or None if not found
        """
        for property_data in self._properties_data:
            if property_data.get("unitId") == unit_id:
                return property_data
        return None
    
    def get_properties_by_group_id(self, group_id: str) -> List[Dict[str, Any]]:
        """
        Get all properties that belong to a specific group.
        
        Args:
            group_id: The group ID to search for
            
        Returns:
            List of property data dictionaries belonging to the group
        """
        matching_properties = []
        for property_data in self._properties_data:
            group_ids = property_data.get("groupIds", [])
            if group_id in group_ids:
                matching_properties.append(property_data)
        return matching_properties
    
    def search_properties_by_criteria(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search properties based on various criteria with exact matching.
        
        Args:
            **criteria: Search criteria such as:
            - number_of_bedrooms: int (exact match, e.g., 2 for "2-bedroom")
            - number_of_bathrooms: int (exact match, e.g., 2 for "2-bathroom")
            - min_area: float (minimum gross floor area in m², e.g., 50.0)
            - max_area: float (maximum gross floor area in m², e.g., 120.0)
            - min_price: float (minimum total price, e.g., 2000000000 for 2 billion VND)
            - max_price: float (maximum total price, e.g., 5000000000 for 5 billion VND)
            - has_balcony: bool (True if balcony required, False if not allowed)
            - furnished: bool (True if furnished required, False if unfurnished required)
            
        Returns:
            List of property data dictionaries matching ALL specified criteria
            
        Example:
            # Find 2-bedroom apartments with balcony, 50-100 sqm, under 3 billion VND
            search_properties_by_criteria(
                number_of_bedrooms=2,
                min_area=50.0,
                max_area=100.0,
                max_price=3000000000,
                has_balcony=True
            )
        """
        matching_properties = []
        
        for property_data in self._properties_data:
            if self._property_matches_criteria(property_data, criteria):
                matching_properties.append(property_data)
        
        return matching_properties
    
    def _property_matches_criteria(self, property_data: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if a property matches the given criteria."""
        try:
            # Get property features
            features = property_data.get("data", {}).get("physical_features", {}).get("value", [])
            
            # Extract relevant values
            property_values = {}
            for feature in features:
                key = feature.get("key")
                value = feature.get("value")
                property_values[key] = value
            
            # Check each criterion
            for criterion, expected_value in criteria.items():
                if criterion == "number_of_bedrooms":
                    if property_values.get("number_of_bedrooms") != expected_value:
                        return False
                        
                elif criterion == "number_of_bathrooms":
                    if property_values.get("number_of_bathrooms") != expected_value:
                        return False
                        
                elif criterion == "min_area":
                    area = property_values.get("gross_floor_area", 0)
                    if area < expected_value:
                        return False
                        
                elif criterion == "max_area":
                    area = property_values.get("gross_floor_area", float('inf'))
                    if area > expected_value:
                        return False
                        
                elif criterion == "has_balcony":
                    has_balcony = property_values.get("has_balcony_or_logia", False)
                    if has_balcony != expected_value:
                        return False
                        
                elif criterion == "furnished":
                    furnished = property_values.get("furnished", False)
                    if furnished != expected_value:
                        return False
                        
                elif criterion == "min_price":
                    price = property_values.get("total_price", 0)
                    if price < expected_value:
                        return False
                        
                elif criterion == "max_price":
                    price = property_values.get("total_price", float('inf'))
                    if price > expected_value:
                        return False
            
            return True
            
        except Exception:
            # If there's any error in parsing, consider it as not matching
            return False
    
    def get_project_overview_by_name(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Get project overview by project name.
        
        Args:
            project_name: Name of the project to search for
            
        Returns:
            Project overview data or None if not found
        """
        for group_data in self._property_groups_data:
            project_overview = group_data.get("project_overview", {}).get("value", [])
            for item in project_overview:
                if (item.get("key") == "project_name" and 
                    project_name.lower() in item.get("value", "").lower()):
                    return group_data
        return None
    
    def get_project_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all projects.
        
        Returns:
            Dictionary containing project statistics
        """
        stats = {
            "total_properties": len(self._properties_data),
            "total_projects": len(self._property_groups_data),
            "properties_by_type": {},
            "price_ranges": {"min": None, "max": None, "average": None},
            "area_ranges": {"min": None, "max": None, "average": None}
        }
        
        # Analyze properties
        areas = []
        prices = []
        
        for property_data in self._properties_data:
            try:
                features = property_data.get("data", {}).get("physical_features", {}).get("value", [])
                for feature in features:
                    if feature.get("key") == "gross_floor_area":
                        area = feature.get("value")
                        if area:
                            areas.append(area)
                    elif feature.get("key") == "total_price":
                        price = feature.get("value")
                        if price:
                            prices.append(price)
            except Exception:
                continue
        
        # Calculate statistics
        if areas:
            stats["area_ranges"]["min"] = min(areas)
            stats["area_ranges"]["max"] = max(areas)
            stats["area_ranges"]["average"] = sum(areas) / len(areas)
        
        if prices:
            stats["price_ranges"]["min"] = min(prices)
            stats["price_ranges"]["max"] = max(prices)
            stats["price_ranges"]["average"] = sum(prices) / len(prices)
        
        return stats
    
    def get_property_summary(self, unit_id: str) -> Dict[str, Any]:
        """
        Get a human-readable summary of a property.
        
        Args:
            unit_id: The unit ID of the property
            
        Returns:
            Dictionary containing a formatted summary of the property
        """
        property_data = self.get_property_by_id(unit_id)
        if not property_data:
            return {"error": f"Property with ID {unit_id} not found"}
        
        summary = {
            "unit_id": unit_id,
            "description": property_data.get("description", ""),
            "group_ids": property_data.get("groupIds", []),
            "features": {}
        }
        
        try:
            features = property_data.get("data", {}).get("physical_features", {}).get("value", [])
            for feature in features:
                key = feature.get("key", "")
                label = feature.get("label", "")
                value = feature.get("value")
                unit = feature.get("unit", "")
                important = feature.get("important", False)
                
                if value is not None:
                    summary["features"][key] = {
                        "label": label,
                        "value": value,
                        "unit": unit,
                        "important": important
                    }
        except Exception as e:
            summary["error"] = f"Error parsing property features: {e}"
        
        return summary
    
    def search_projects_by_criteria(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search projects based on various criteria.
        
        Args:
            **criteria: Search criteria such as:
                - location: str (search in location fields)
                - developer: str (search in developer name)
                - status: str (project status)
                - min_units: int (minimum number of units)
                - segment: str (market segment)
                
        Returns:
            List of project data dictionaries matching the criteria
        """
        matching_projects = []
        
        for project_data in self._property_groups_data:
            if self._project_matches_criteria(project_data, criteria):
                matching_projects.append(project_data)
        
        return matching_projects
    
    def _project_matches_criteria(self, project_data: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if a project matches the given criteria."""
        try:
            # Convert project data to a searchable string for text-based searches
            project_text = json.dumps(project_data, ensure_ascii=False).lower()
            
            for criterion, expected_value in criteria.items():
                expected_lower = str(expected_value).lower()
                
                if criterion == "location":
                    # Search in location-related fields
                    location_fields = project_data.get("location_and_surrounding_amenities", {})
                    location_text = json.dumps(location_fields, ensure_ascii=False).lower()
                    if expected_lower not in location_text:
                        return False
                        
                elif criterion == "developer":
                    # Search in developer fields
                    developer_fields = project_data.get("developer", {})
                    developer_text = json.dumps(developer_fields, ensure_ascii=False).lower()
                    if expected_lower not in developer_text:
                        return False
                        
                elif criterion == "status":
                    # Search in project overview status
                    overview = project_data.get("project_overview", {}).get("value", [])
                    status_found = False
                    for item in overview:
                        if item.get("key") == "status" and expected_lower in str(item.get("value", "")).lower():
                            status_found = True
                            break
                    if not status_found:
                        return False
                        
                elif criterion == "segment":
                    # Search in project segment
                    overview = project_data.get("project_overview", {}).get("value", [])
                    segment_found = False
                    for item in overview:
                        if item.get("key") == "segment" and expected_lower in str(item.get("value", "")).lower():
                            segment_found = True
                            break
                    if not segment_found:
                        return False
                        
                else:
                    # Generic text search
                    if expected_lower not in project_text:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def get_project_amenities(self, group_index: int = 0) -> Dict[str, Any]:
        """
        Get amenities information for a project.
        
        Args:
            group_index: Index of the project group (default: 0)
            
        Returns:
            Dictionary containing project amenities information
        """
        if group_index >= len(self._property_groups_data):
            return {"error": "Project group index out of range"}
        
        project_data = self._property_groups_data[group_index]
        amenities = {}
        
        # Extract internal amenities
        try:
            overview = project_data.get("project_overview", {}).get("value", [])
            for item in overview:
                if item.get("key") == "internal_amenities":
                    amenities["internal_amenities"] = item.get("value", [])
                    break
        except Exception:
            pass
        
        # Extract surrounding amenities
        try:
            location_data = project_data.get("location_and_surrounding_amenities", {}).get("value", [])
            for item in location_data:
                if item.get("key") == "surrounding_amenities":
                    amenities["surrounding_amenities"] = item.get("value", [])
                    break
        except Exception:
            pass
        
        return amenities


# Convenience functions for easy integration with the chat agent
def create_real_estate_tools(mock_data_dir: str = None) -> RealEstateDataTools:
    """
    Create and return a RealEstateDataTools instance.
    
    Args:
        mock_data_dir: Optional path to mock data directory
        
    Returns:
        RealEstateDataTools instance
    """
    return RealEstateDataTools(mock_data_dir)


def get_property_search_help() -> str:
    """
    Return help text for property search functionality.
    
    Returns:
        Help text string
    """
    return """
Available property search criteria:
- number_of_bedrooms: Number of bedrooms (integer, exact match)
- number_of_bathrooms: Number of bathrooms (integer, exact match)
- min_area: Minimum gross floor area in m² (float)
- max_area: Maximum gross floor area in m² (float)
- min_price: Minimum price in local currency (float)
- max_price: Maximum price in local currency (float)
- has_balcony: Whether property has balcony/logia (boolean)
- furnished: Whether property is furnished (boolean)

PRICE CONVERSION GUIDE:
- Vietnamese: "3 tỷ VND" = 3000000000 (3 billion)
- Vietnamese: "500 triệu VND" = 500000000 (500 million)
- US Dollar: "$300k" = 300000

EXAMPLE SEARCHES:
- 2-bedroom with balcony: number_of_bedrooms=2, has_balcony=True
- Under 3 billion VND: max_price=3000000000
- 50-100 sqm: min_area=50.0, max_area=100.0
- Budget 2-4 billion: min_price=2000000000, max_price=4000000000

Example usage:
tools.search_properties_by_criteria(number_of_bedrooms=2, min_area=50, has_balcony=True)
"""


def get_project_search_help() -> str:
    """
    Return help text for project search functionality.
    
    Returns:
        Help text string
    """
    return """
Available project search criteria:
- location: Search text in location fields (string)
- developer: Search text in developer fields (string)
- status: Project status (string)
- segment: Market segment (string)

Example usage:
tools.search_projects_by_criteria(developer="Vinhomes", status="đang mở bán")
"""


# Global instance for function calling
_global_tools = None
_global_preference_manager = None

def get_global_tools() -> RealEstateDataTools:
    """Get or create the global tools instance."""
    global _global_tools
    if _global_tools is None:
        _global_tools = RealEstateDataTools()
    return _global_tools


def get_global_preference_manager() -> UserPreferenceManager:
    """Get or create the global preference manager instance."""
    global _global_preference_manager
    if _global_preference_manager is None:
        _global_preference_manager = UserPreferenceManager()
    return _global_preference_manager


# Function calling tools for AutoGen
def search_properties_by_criteria(
    number_of_bedrooms: Annotated[Optional[int], "Exact number of bedrooms required (e.g., 1, 2, 3)"] = None,
    number_of_bathrooms: Annotated[Optional[int], "Exact number of bathrooms required (e.g., 1, 2, 3)"] = None,
    min_area: Annotated[Optional[float], "Minimum gross floor area in square meters (e.g., 50.0 for 50 sqm)"] = None,
    max_area: Annotated[Optional[float], "Maximum gross floor area in square meters (e.g., 120.0 for 120 sqm)"] = None,
    min_price: Annotated[Optional[float], "Minimum price in the property's currency (e.g., 2000000000 for 2 billion VND)"] = None,
    max_price: Annotated[Optional[float], "Maximum price in the property's currency (e.g., 5000000000 for 5 billion VND)"] = None,
    has_balcony: Annotated[Optional[bool], "Whether property must have a balcony or logia (True/False)"] = None,
    furnished: Annotated[Optional[bool], "Whether property must be furnished (True/False)"] = None,
) -> List[Dict[str, Any]]:
    """
    Search for properties in the database based on specific criteria. Use this function when users want to:
    - Find properties matching specific requirements
    - Search for apartments/condos/houses with certain features
    - Look for properties within a budget range
    - Find properties with specific room counts or sizes
    
    IMPORTANT USAGE GUIDELINES:
    - Use exact numbers for bedrooms/bathrooms (e.g., number_of_bedrooms=2 for "2-bedroom")
    - For price searches, use the actual currency amounts (VND prices are typically in billions)
    - Area is in square meters (common range: 30-200 sqm for apartments)
    - Set has_balcony=True only if user specifically mentions wanting a balcony
    - Set furnished=True only if user specifically mentions wanting furnished property
    
    EXAMPLES:
    - "2-bedroom apartment" → number_of_bedrooms=2
    - "under 3 billion VND" → max_price=3000000000
    - "at least 80 sqm" → min_area=80.0
    - "with balcony" → has_balcony=True
    - "budget 2-4 billion" → min_price=2000000000, max_price=4000000000
    
    Args:
        number_of_bedrooms: Exact number of bedrooms (1, 2, 3, etc.)
        number_of_bathrooms: Exact number of bathrooms (1, 2, 3, etc.)
        min_area: Minimum size in square meters
        max_area: Maximum size in square meters  
        min_price: Minimum price in local currency (VND/USD/etc.)
        max_price: Maximum price in local currency (VND/USD/etc.)
        has_balcony: Must have balcony/logia (True) or doesn't matter (None)
        furnished: Must be furnished (True) or doesn't matter (None)
    
    Returns:
        List of property dictionaries matching ALL specified criteria
    """
    tools = get_global_tools()
    criteria = {}
    if number_of_bedrooms is not None:
        criteria['number_of_bedrooms'] = number_of_bedrooms
    if number_of_bathrooms is not None:
        criteria['number_of_bathrooms'] = number_of_bathrooms
    if min_area is not None:
        criteria['min_area'] = min_area
    if max_area is not None:
        criteria['max_area'] = max_area
    if min_price is not None:
        criteria['min_price'] = min_price
    if max_price is not None:
        criteria['max_price'] = max_price
    if has_balcony is not None:
        criteria['has_balcony'] = has_balcony
    if furnished is not None:
        criteria['furnished'] = furnished
    
    return tools.search_properties_by_criteria(**criteria)


def get_property_by_id(
    unit_id: Annotated[str, "The unit ID of the property to retrieve"]
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific property by its unit ID.
    
    Returns:
        Property data dictionary or None if not found
    """
    tools = get_global_tools()
    return tools.get_property_by_id(unit_id)


def get_property_summary(
    unit_id: Annotated[str, "The unit ID of the property to get summary for"]
) -> Dict[str, Any]:
    """
    Get a human-readable summary of a property including key features.
    
    Returns:
        Dictionary containing formatted property summary
    """
    tools = get_global_tools()
    return tools.get_property_summary(unit_id)


def search_projects_by_criteria(
    location: Annotated[Optional[str], "Search text in location fields"] = None,
    developer: Annotated[Optional[str], "Search text in developer fields"] = None,
    status: Annotated[Optional[str], "Project status"] = None,
    segment: Annotated[Optional[str], "Market segment"] = None,
) -> List[Dict[str, Any]]:
    """
    Search for real estate projects based on specified criteria.
    
    Returns:
        List of projects matching the criteria
    """
    tools = get_global_tools()
    criteria = {}
    if location is not None:
        criteria['location'] = location
    if developer is not None:
        criteria['developer'] = developer
    if status is not None:
        criteria['status'] = status
    if segment is not None:
        criteria['segment'] = segment
    
    return tools.search_projects_by_criteria(**criteria)


def get_project_statistics() -> Dict[str, Any]:
    """
    Get comprehensive statistics about all projects and properties in the database.
    
    Returns:
        Dictionary containing statistics like total properties, price ranges, area ranges
    """
    tools = get_global_tools()
    return tools.get_project_statistics()


def get_project_amenities(
    group_index: Annotated[int, "Index of the project group (default: 0)"] = 0
) -> Dict[str, Any]:
    """
    Get amenities information for a specific project.
    
    Returns:
        Dictionary containing internal and surrounding amenities
    """
    tools = get_global_tools()
    return tools.get_project_amenities(group_index)


def get_properties_by_group_id(
    group_id: Annotated[str, "The group ID to search for"]
) -> List[Dict[str, Any]]:
    """
    Get all properties that belong to a specific project group.
    
    Returns:
        List of properties in the specified group
    """
    tools = get_global_tools()
    return tools.get_properties_by_group_id(group_id)


def get_all_properties() -> List[Dict[str, Any]]:
    """
    Get all properties from the database.
    
    Returns:
        List of all property data
    """
    tools = get_global_tools()
    return tools.get_all_properties()


def get_all_property_groups() -> List[Dict[str, Any]]:
    """
    Get all property groups/projects from the database.
    
    Returns:
        List of all project data
    """
    tools = get_global_tools()
    return tools.get_all_property_groups()


# User Preference Management Function Calling Tools
def update_user_profile(
    name: Annotated[Optional[str], "User's full name"] = None,
    phone_number: Annotated[Optional[str], "User's phone number"] = None,
    email: Annotated[Optional[str], "User's email address"] = None,
    age: Annotated[Optional[int], "User's age"] = None
) -> Dict[str, Any]:
    """
    Update user profile information in the preferences file.
    
    Args:
        name: User's full name
        phone_number: User's phone number
        email: User's email address
        age: User's age
    
    Returns:
        Updated user profile information
    """
    preference_manager = get_global_preference_manager()
    
    # Filter out None values
    updates = {k: v for k, v in locals().items() if v is not None and k != 'preference_manager'}
    
    if updates:
        preference_manager.update_user_profile(**updates)
        return {
            "status": "success",
            "message": f"Updated user profile: {list(updates.keys())}",
            "updated_profile": preference_manager.get_user_profile()
        }
    else:
        return {
            "status": "no_updates",
            "message": "No profile updates provided",
            "current_profile": preference_manager.get_user_profile()
        }


def update_property_preferences(
    property_type: Annotated[Optional[List[str]], "List of preferred property types (e.g., ['apartment', 'condo'])"] = None,
    budget_min: Annotated[Optional[float], "Minimum budget"] = None,
    budget_max: Annotated[Optional[float], "Maximum budget"] = None,
    currency: Annotated[Optional[str], "Currency (e.g., 'VND', 'USD')"] = None,
    locations: Annotated[Optional[List[str]], "List of preferred locations"] = None,
    bedrooms_min: Annotated[Optional[int], "Minimum number of bedrooms"] = None,
    bedrooms_max: Annotated[Optional[int], "Maximum number of bedrooms"] = None,
    bathrooms_min: Annotated[Optional[int], "Minimum number of bathrooms"] = None,
    size_min_sqm: Annotated[Optional[float], "Minimum size in square meters"] = None,
    size_max_sqm: Annotated[Optional[float], "Maximum size in square meters"] = None,
    must_have_amenities: Annotated[Optional[List[str]], "List of required amenities"] = None,
    nice_to_have_amenities: Annotated[Optional[List[str]], "List of preferred amenities"] = None
) -> Dict[str, Any]:
    """
    Update property preferences in the preferences file.
    
    Args:
        property_type: List of preferred property types
        budget_min: Minimum budget
        budget_max: Maximum budget
        currency: Currency preference
        locations: List of preferred locations
        bedrooms_min: Minimum number of bedrooms
        bedrooms_max: Maximum number of bedrooms
        bathrooms_min: Minimum number of bathrooms
        size_min_sqm: Minimum size in square meters
        size_max_sqm: Maximum size in square meters
        must_have_amenities: List of required amenities
        nice_to_have_amenities: List of preferred amenities
    
    Returns:
        Updated property preferences
    """
    preference_manager = get_global_preference_manager()
    
    # Filter out None values
    updates = {k: v for k, v in locals().items() if v is not None and k != 'preference_manager'}
    
    if updates:
        preference_manager.update_property_preferences(**updates)
        return {
            "status": "success",
            "message": f"Updated property preferences: {list(updates.keys())}",
            "updated_preferences": preference_manager.get_property_preferences()
        }
    else:
        return {
            "status": "no_updates",
            "message": "No property preference updates provided",
            "current_preferences": preference_manager.get_property_preferences()
        }


def get_user_preferences() -> Dict[str, Any]:
    """
    Get all current user preferences from the preferences file.
    
    Returns:
        Complete user preferences including profile and property preferences
    """
    preference_manager = get_global_preference_manager()
    return {
        "status": "success",
        "preferences": preference_manager.get_preferences()
    }


def add_search_to_history(
    search_criteria: Annotated[Dict[str, Any], "The search criteria used"]
) -> Dict[str, Any]:
    """
    Add a property search to the user's search history.
    
    Args:
        search_criteria: Dictionary containing the search parameters used
    
    Returns:
        Confirmation of search history update
    """
    preference_manager = get_global_preference_manager()
    preference_manager.add_to_search_history(search_criteria)
    
    return {
        "status": "success",
        "message": "Search added to history",
        "search_criteria": search_criteria
    }


def update_recent_interests(
    interests: Annotated[List[str], "List of recent property interests or keywords mentioned by user"]
) -> Dict[str, Any]:
    """
    Update the user's recent interests based on conversation context.
    
    Args:
        interests: List of recent interests, keywords, or topics the user mentioned
    
    Returns:
        Updated conversation context
    """
    preference_manager = get_global_preference_manager()
    preference_manager.update_conversation_context(recent_interests=interests)
    
    return {
        "status": "success",
        "message": "Recent interests updated",
        "interests": interests
    }


# List of all function calling tools
REAL_ESTATE_TOOLS = [
    # search_properties_by_criteria,
    # get_property_by_id,
    # get_property_summary,
    # search_projects_by_criteria,
    # get_project_statistics,
    # get_project_amenities,
    # get_properties_by_group_id,
    # get_all_properties,
    # get_all_property_groups,
    # User preference management tools
    update_user_profile,
    update_property_preferences,
    get_user_preferences,
    add_search_to_history,
    update_recent_interests,
]
