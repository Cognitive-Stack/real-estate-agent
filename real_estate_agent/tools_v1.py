"""
Real Estate Data Query Tools

This module provides tools for the real estate agent to query and analyze
property data and property group data from mock data sources.
"""

import json
import os
from typing import List, Dict, Any, Optional, Union, Annotated
from pathlib import Path


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
        Search properties based on various criteria.
        
        Args:
            **criteria: Search criteria such as:
                - number_of_bedrooms: int
                - number_of_bathrooms: int
                - min_area: float (minimum gross floor area)
                - max_area: float (maximum gross floor area)
                - min_price: float (minimum price)
                - max_price: float (maximum price)
                - has_balcony: bool
                - furnished: bool
                
        Returns:
            List of property data dictionaries matching the criteria
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
- number_of_bedrooms: Number of bedrooms (integer)
- number_of_bathrooms: Number of bathrooms (integer)
- min_area: Minimum gross floor area in m² (float)
- max_area: Maximum gross floor area in m² (float)
- has_balcony: Whether property has balcony/logia (boolean)
- furnished: Whether property is furnished (boolean)

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

def get_global_tools() -> RealEstateDataTools:
    """Get or create the global tools instance."""
    global _global_tools
    if _global_tools is None:
        _global_tools = RealEstateDataTools()
    return _global_tools


# Function calling tools for AutoGen
def search_properties_by_criteria(
    number_of_bedrooms: Annotated[Optional[int], "Number of bedrooms"] = None,
    number_of_bathrooms: Annotated[Optional[int], "Number of bathrooms"] = None,
    min_area: Annotated[Optional[float], "Minimum gross floor area in m²"] = None,
    max_area: Annotated[Optional[float], "Maximum gross floor area in m²"] = None,
    has_balcony: Annotated[Optional[bool], "Whether property has balcony/logia"] = None,
    furnished: Annotated[Optional[bool], "Whether property is furnished"] = None,
) -> List[Dict[str, Any]]:
    """
    Search for properties based on specified criteria.
    
    Returns:
        List of properties matching the criteria
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


# List of all function calling tools
REAL_ESTATE_TOOLS = [
    search_properties_by_criteria,
    get_property_by_id,
    get_property_summary,
    search_projects_by_criteria,
    get_project_statistics,
    get_project_amenities,
    get_properties_by_group_id,
    get_all_properties,
    get_all_property_groups,
]
