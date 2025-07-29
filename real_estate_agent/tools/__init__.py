from .contractors import ContractorsTools
from .developers import DevelopersTools
from .locations import LocationsTools
from .project_overview import ProjectOverviewTools
from .physical_features import PhysicalFeaturesTools
from .investment_info import InvestmentInfoTools
from .legal_info import LegalInfoTools
from .sales_policy import SalesPolicyTools
from .transportation import TransportationTools
from .residential_environment import ResidentialEnvironmentTools
from .living_experience import LivingExperienceTools
from .design_layout import DesignLayoutTools
from .equipment_materials import EquipmentMaterialsTools
from .legal_status import LegalStatusTools
from .properties import PropertiesTools
from typing import List, Dict, Any, Optional, Annotated

# Create global instances of tool classes
_contractors_tools = ContractorsTools()
_developers_tools = DevelopersTools()
_locations_tools = LocationsTools()
_project_overview_tools = ProjectOverviewTools()
_physical_features_tools = PhysicalFeaturesTools()
_investment_info_tools = InvestmentInfoTools()
_legal_info_tools = LegalInfoTools()
_sales_policy_tools = SalesPolicyTools()
_transportation_tools = TransportationTools()
_residential_environment_tools = ResidentialEnvironmentTools()
_living_experience_tools = LivingExperienceTools()
_design_layout_tools = DesignLayoutTools()
_equipment_materials_tools = EquipmentMaterialsTools()
_properties_tools = PropertiesTools()
_legal_status_tools = LegalStatusTools()

# Wrapper functions for autogen compatibility
def search_contractors(
    name: Annotated[Optional[str], "Contractor name"] = None,
    capacity: Annotated[Optional[str], "Capacity/scale"] = None,
    certificate: Annotated[Optional[str], "Professional certificates"] = None,
    project: Annotated[Optional[str], "Previous projects"] = None,
    material: Annotated[Optional[str], "Material quality"] = None,
    technology: Annotated[Optional[str], "Applied technology"] = None,
    philosophy: Annotated[Optional[str], "Design philosophy"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for contractors based on specified criteria."""
    criteria = {}
    if name is not None:
        criteria['name'] = name
    if capacity is not None:
        criteria['capacity'] = capacity
    if certificate is not None:
        criteria['certificate'] = certificate
    if project is not None:
        criteria['project'] = project
    if material is not None:
        criteria['material'] = material
    if technology is not None:
        criteria['technology'] = technology
    if philosophy is not None:
        criteria['philosophy'] = philosophy
    if general is not None:
        criteria['general'] = general
    return _contractors_tools.search_contractors(**criteria)

def search_developers(
    name: Annotated[Optional[str], "Developer name"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for developers based on specified criteria."""
    criteria = {}
    if name is not None:
        criteria['name'] = name
    if general is not None:
        criteria['general'] = general
    return _developers_tools.search_developers(**criteria)

def search_locations(
    name: Annotated[Optional[str], "Location name"] = None,
    district: Annotated[Optional[str], "District"] = None,
    province: Annotated[Optional[str], "Province"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for locations based on specified criteria."""
    criteria = {}
    if name is not None:
        criteria['name'] = name
    if district is not None:
        criteria['district'] = district
    if province is not None:
        criteria['province'] = province
    if general is not None:
        criteria['general'] = general
    return _locations_tools.search_locations(**criteria)

def search_project_overview(
    name: Annotated[Optional[str], "Project name"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for project overview information based on specified criteria."""
    criteria = {}
    if name is not None:
        criteria['name'] = name
    if general is not None:
        criteria['general'] = general
    return _project_overview_tools.search_project_overview(**criteria)

def search_physical_features(
    feature: Annotated[Optional[str], "Physical feature"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for physical features based on specified criteria."""
    criteria = {}
    if feature is not None:
        criteria['feature'] = feature
    if general is not None:
        criteria['general'] = general
    return _physical_features_tools.search_physical_features(**criteria)

def search_investment_info(
    price: Annotated[Optional[str], "Price information"] = None,
    payment: Annotated[Optional[str], "Payment terms"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for investment information based on specified criteria."""
    criteria = {}
    if price is not None:
        criteria['price'] = price
    if payment is not None:
        criteria['payment'] = payment
    if general is not None:
        criteria['general'] = general
    return _investment_info_tools.search_investment_info(**criteria)

def search_legal_info(
    legal_type: Annotated[Optional[str], "Type of legal information"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for legal information based on specified criteria."""
    criteria = {}
    if legal_type is not None:
        criteria['legal_type'] = legal_type
    if general is not None:
        criteria['general'] = general
    return _legal_info_tools.search_legal_info(**criteria)

def search_sales_policy(
    policy_type: Annotated[Optional[str], "Type of sales policy"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for sales policy information based on specified criteria."""
    criteria = {}
    if policy_type is not None:
        criteria['policy_type'] = policy_type
    if general is not None:
        criteria['general'] = general
    return _sales_policy_tools.search_sales_policy(**criteria)

def search_transportation(
    transport_type: Annotated[Optional[str], "Type of transportation"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for transportation information based on specified criteria."""
    criteria = {}
    if transport_type is not None:
        criteria['transport_type'] = transport_type
    if general is not None:
        criteria['general'] = general
    return _transportation_tools.search_transportation(**criteria)

def search_residential_environment(
    environment_type: Annotated[Optional[str], "Type of residential environment"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for residential environment information based on specified criteria."""
    criteria = {}
    if environment_type is not None:
        criteria['environment_type'] = environment_type
    if general is not None:
        criteria['general'] = general
    return _residential_environment_tools.search_residential_environment(**criteria)

def search_living_experience(
    experience_type: Annotated[Optional[str], "Type of living experience"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for living experience information based on specified criteria."""
    criteria = {}
    if experience_type is not None:
        criteria['experience_type'] = experience_type
    if general is not None:
        criteria['general'] = general
    return _living_experience_tools.search_living_experience(**criteria)

def search_design_layout(
    layout_type: Annotated[Optional[str], "Type of design layout"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for design layout information based on specified criteria."""
    criteria = {}
    if layout_type is not None:
        criteria['layout_type'] = layout_type
    if general is not None:
        criteria['general'] = general
    return _design_layout_tools.search_design_layout(**criteria)

def search_equipment_materials(
    equipment_type: Annotated[Optional[str], "Type of equipment or material"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for equipment and materials information based on specified criteria."""
    criteria = {}
    if equipment_type is not None:
        criteria['equipment_type'] = equipment_type
    if general is not None:
        criteria['general'] = general
    return _equipment_materials_tools.search_equipment_materials(**criteria)

def search_legal_status(
    status_type: Annotated[Optional[str], "Type of legal status"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for legal status information based on specified criteria."""
    criteria = {}
    if status_type is not None:
        criteria['status_type'] = status_type
    if general is not None:
        criteria['general'] = general
    return _legal_status_tools.search_legal_status(**criteria)

def search_properties(
    property_type: Annotated[Optional[str], "Type of property"] = None,
    location: Annotated[Optional[str], "Location of the property"] = None,
    price_range: Annotated[Optional[str], "Price range"] = None,
    general: Annotated[Optional[str], "General search across all fields"] = None,
) -> List[Dict[str, Any]]:
    """Search for properties based on specified criteria."""
    criteria = {}
    if property_type is not None:
        criteria['property_type'] = property_type
    if location is not None:
        criteria['location'] = location
    if price_range is not None:
        criteria['price_range'] = price_range
    if general is not None:
        criteria['general'] = general
    return _properties_tools.search_properties(**criteria)

# List of all function calling tools
REAL_ESTATE_TOOLS = [
    search_contractors,
    search_developers,
    search_locations,
    search_project_overview,
    search_physical_features,
    search_investment_info,
    search_legal_info,
    search_sales_policy,
    search_transportation,
    search_residential_environment,
    search_living_experience,
    search_design_layout,
    search_equipment_materials,
    search_legal_status,
    search_properties
]