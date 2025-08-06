# Multi-Modal Data Extractor using autogen agentchat 0.6.2
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import PIL
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import MultiModalMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import Image
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient
from autogen_ext.auth.azure import AzureTokenProvider
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Azure configuration from environment variables
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# Validate required environment variables
if not AZURE_OPENAI_DEPLOYMENT:
    raise ValueError("AZURE_OPENAI_DEPLOYMENT environment variable is required")
if not AZURE_OPENAI_ENDPOINT:
    raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
if not AZURE_OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")


# Initialize Azure OpenAI client
model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    model=AZURE_OPENAI_MODEL,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

# model_client = OpenAIChatCompletionClient(
#     model="gpt-4o",
#     # model_info=ModelInfo(vision=True, function_calling=True, json_output=True, family="unknown", structured_output=True),
# )

# Define structured output for real estate project data
# Nested models for location and surrounding amenities
class ExactLocationOnMap(BaseModel):
    longitude: float = Field(description="Longitude coordinate")
    latitude: float = Field(description="Latitude coordinate")

class Planning(BaseModel):
    current: str = Field(description="Current planning status and details")
    ten_years: str = Field(description="10-year future planning vision")

class SurroundingAmenities(BaseModel):
    school_distance: str = Field(description="Distance to schools and educational facilities")

class LocationAndSurroundingAmenities(BaseModel):
    exact_location_on_map: ExactLocationOnMap = Field(description="Exact GPS coordinates")
    planning: Planning = Field(description="Current and future planning details")
    surrounding_amenities: SurroundingAmenities = Field(description="Nearby amenities and facilities")

# Nested models for transportation infrastructure
class TrafficConditions(BaseModel):
    normal_hours: str = Field(description="Traffic conditions during normal hours")
    peak_hours: str = Field(description="Traffic conditions during peak hours")

class TransportationInfrastructure(BaseModel):
    main_roads_ring_roads_major_intersections: str = Field(description="Main roads, ring roads, and major intersections")
    current_road_condition: str = Field(description="Current condition of roads")
    planned_upgrades: str = Field(description="Planned road upgrades and improvements")
    interprovincial_intercity_connection: str = Field(description="Connections to other provinces and cities")
    traffic_conditions: TrafficConditions = Field(description="Traffic conditions analysis")
    regional_connectivity: str = Field(description="Regional connectivity information")

# Nested models for residential environment and security
class SecuritySystem(BaseModel):
    low_crime_rate: bool = Field(description="Low crime rate indicator")
    security_24_7: bool = Field(description="24/7 security service")
    security_cameras: bool = Field(description="Security camera system")
    access_card: bool = Field(description="Access card system")
    control_checkpoint: bool = Field(description="Control checkpoint system")

class ResidentialEnvironmentAndSecurity(BaseModel):
    resident_type: str = Field(description="Type of residents in the area")
    quietness_level: str = Field(description="Level of quietness and tranquility")
    near_market: bool = Field(description="Proximity to markets")
    community_intellectual_and_civilization_level: str = Field(description="Community intellectual and civilization level")
    security_system: SecuritySystem = Field(description="Security system features")

# Nested models for developer
class ProjectList(BaseModel):
    project_1: str = Field(description="First project in the list")

class Developer(BaseModel):
    name: str = Field(description="Developer company name")
    year_founded: int = Field(description="Year the developer was founded")
    financial_capacity: str = Field(description="Financial capacity description")
    completed_projects: ProjectList = Field(description="List of completed projects")
    projects_for_sale: ProjectList = Field(description="List of projects currently for sale")
    upcoming_projects: ProjectList = Field(description="List of upcoming projects")
    quality_assessment: str = Field(description="Quality assessment of the developer")
    legal_assessment: str = Field(description="Legal compliance assessment")

# Nested models for legal
class Legal(BaseModel):
    ownership_certificate: str = Field(description="Ownership certificate details")
    bank_guarantee_for_off_plan_properties: str = Field(description="Bank guarantee for off-plan properties")
    construction_permit: str = Field(description="Construction permit status")
    land_allocation_decision: str = Field(description="Land allocation decision details")
    foundation_acceptance_certificate: str = Field(description="Foundation acceptance certificate status")
    document_of_eligibility_for_sale: str = Field(description="Document of eligibility for sale")
    sample_contract: str = Field(description="Sample contract details")
    transfer_terms: str = Field(description="Transfer terms and conditions")
    progress_commitment: str = Field(description="Progress commitment details")
    handover_commitment: str = Field(description="Handover commitment details")
    late_payment_penalty: str = Field(description="Late payment penalty terms")
    planning_text: str = Field(description="Planning text details")
    planning_images: List[str] = Field(description="Planning images list")

# Nested models for construction contractor
class ConstructionContractor(BaseModel):
    contractor_name: str = Field(description="Name of construction contractor")
    capacity_scale: str = Field(description="Capacity and scale of the contractor")
    professional_practice_certificate: str = Field(description="Professional practice certificate details")
    previous_completed_projects: ProjectList = Field(description="Previous completed projects")
    material_quality: str = Field(description="Material quality description")
    applied_technology: str = Field(description="Applied technology details")
    design_philosophy: str = Field(description="Design philosophy")

# Nested models for interior design unit
class InteriorDesignUnit(BaseModel):
    contractor_name: str = Field(description="Name of interior design contractor")
    capacity_scale: str = Field(description="Capacity and scale of the interior design unit")
    professional_practice_certificate: str = Field(description="Professional practice certificate details")
    previous_completed_projects: ProjectList = Field(description="Previous completed projects")
    material_quality: str = Field(description="Material quality description")
    applied_technology: str = Field(description="Applied technology details")
    design_philosophy: str = Field(description="Design philosophy")

# Nested models for management unit
class ServicesProvided(BaseModel):
    technical_maintenance: str = Field(description="Technical maintenance services")
    security: str = Field(description="Security services")
    cleaning_sanitation: str = Field(description="Cleaning and sanitation services")

class ManagementUnit(BaseModel):
    management_unit_name: str = Field(description="Name of the management unit")
    management_fee: str = Field(description="Management fee details")
    services_provided: ServicesProvided = Field(description="Services provided by management")
    service_quality: str = Field(description="Quality of services provided")
    fire_prevention_and_fighting: str = Field(description="Fire prevention and fighting systems")

# Nested models for project overview
class TotalNumberOfUnits(BaseModel):
    apartment: int = Field(description="Number of apartments")
    townhouse: int = Field(description="Number of townhouses")
    shophouse: int = Field(description="Number of shophouses")
    villa: int = Field(description="Number of villas")
    officetel: Optional[int] = Field(description="Number of officetels")
    condotel: Optional[int] = Field(description="Number of condotels")
    studio: Optional[int] = Field(description="Number of studios")
    dual_key: Optional[int] = Field(description="Number of dual key units")
    penthouse_skyvilla: Optional[int] = Field(description="Number of penthouses/skyvillas")
    duplex: Optional[int] = Field(description="Number of duplexes")

class ResidentScale(BaseModel):
    current: Optional[int] = Field(description="Current resident population")
    future: int = Field(description="Future projected resident population")

class SellingPrice(BaseModel):
    average: str = Field(description="Average selling price")
    highest: Optional[str] = Field(description="Highest selling price")
    lowest: Optional[str] = Field(description="Lowest selling price")

class RentalPrice(BaseModel):
    average: str = Field(description="Average rental price")
    highest: Optional[str] = Field(description="Highest rental price")
    lowest: Optional[str] = Field(description="Lowest rental price")

class UnitArea(BaseModel):
    smallest: int = Field(description="Smallest unit area")
    largest: int = Field(description="Largest unit area")

class Progress(BaseModel):
    date_04_2025: Optional[str] = Field(description="Progress as of April 2025")

class ProjectOverview(BaseModel):
    project_name: str = Field(description="Name of the project")
    total_land_area: int = Field(description="Total land area in square meters")
    total_number_of_blocks: int = Field(description="Total number of blocks")
    number_of_floors: str = Field(description="Number of floors")
    number_of_basement_floors: int = Field(description="Number of basement floors")
    total_number_of_units: TotalNumberOfUnits = Field(description="Total number of units by type")
    resident_scale: ResidentScale = Field(description="Resident scale information")
    total_investment_capital: Optional[str] = Field(description="Total investment capital")
    selling_price: SellingPrice = Field(description="Selling price information")
    rental_price: RentalPrice = Field(description="Rental price information")
    unit_area: UnitArea = Field(description="Unit area information")
    status: str = Field(description="Project status")
    segment: str = Field(description="Market segment")
    internal_amenities: Optional[str] = Field(description="Internal amenities")
    design_style: str = Field(description="Design style")
    drawings: List[str] = Field(description="Project drawings")
    mockup_images: List[str] = Field(description="Mockup images")
    construction_density: float = Field(description="Construction density percentage")
    land_use_coefficient: Optional[str] = Field(description="Land use coefficient")
    greenery_density: str = Field(description="Greenery density description")
    expected_handover: str = Field(description="Expected handover details")
    progress: Progress = Field(description="Project progress information")

# Nested models for sales policy
class SalesPolicy(BaseModel):
    payment_policy: Optional[str] = Field(description="Payment policy details")
    rental_commitment_for_investment: str = Field(description="Rental commitment for investment")
    estimated_rental_yield: int = Field(description="Estimated rental yield percentage")
    other_gifts: str = Field(description="Other gifts and promotions")

# Nested models for investment and profit potential
class InvestmentAndProfitPotential(BaseModel):
    expected_appreciation_value: str = Field(description="Expected appreciation value")
    current_price_compared_to_area: str = Field(description="Current price compared to area")
    current_supply: str = Field(description="Current supply status")
    number_of_transactions: str = Field(description="Number of transactions")
    ease_of_resale: bool = Field(description="Ease of resale indicator")
    annual_rental_yield: float = Field(description="Annual rental yield percentage")
    rentability: str = Field(description="Rentability assessment")

# Main real estate project data model
class RealEstateProjectData(BaseModel):
    location_and_surrounding_amenities: Optional[LocationAndSurroundingAmenities] = Field(
        description="Location information including coordinates, planning details, and surrounding amenities"
    )
    transportation_infrastructure: Optional[TransportationInfrastructure] = Field(
        description="Transportation details including roads, traffic conditions, and regional connectivity"
    )
    residential_environment_and_security: Optional[ResidentialEnvironmentAndSecurity] = Field(
        description="Residential environment details including security systems and community information"
    )
    developer: Optional[Developer] = Field(
        description="Developer details including name, year founded, financial capacity, and project history"
    )
    legal: Optional[Legal] = Field(
        description="Legal documentation and compliance information for the project"
    )
    construction_contractor: Optional[ConstructionContractor] = Field(
        description="Construction contractor details including name, capacity, and previous projects"
    )
    interior_design_unit: Optional[InteriorDesignUnit] = Field(
        description="Interior design and finishing details"
    )
    management_unit: Optional[ManagementUnit] = Field(
        description="Property management details including fees and services"
    )
    project_overview: Optional[ProjectOverview] = Field(
        description="Comprehensive project information including specifications, pricing, and status"
    )
    sales_policy: Optional[SalesPolicy] = Field(
        description="Sales policies including payment terms and promotional offers"
    )
    investment_and_profit_potential: Optional[InvestmentAndProfitPotential] = Field(
        description="Investment analysis including appreciation potential and rental yields"
    )

# Define structured output for real estate segments
class RealEstateSegments(BaseModel):
    image_name: str = Field(description="The name of the image")
    product_code: str = Field(description="Segment 1: The unique identifier or code for the property unit")
    product_zone: str = Field(description="Segment 2: The zone or area classification of the property")
    construction_area: str = Field(description="Segment 3: The built-up area or construction area in square meters")
    land_area: str = Field(description="Segment 4: The land area or plot size in square meters")
    product_type: str = Field(description="Segment 5: The type of property (e.g., apartment, villa, townhouse, etc.)")
    direction: str = Field(description="Segment 6: The orientation or direction the property faces (e.g., North, South, East, West)")
    price_standard: str = Field(description="Segment 7: The standard selling price of the property")
    price_early: str = Field(description="Segment 8: The early bird or promotional price if available")
    price_loan: str = Field(description="Segment 9: The loan amount or financing information")
    project_branding: str = Field(description="Segment 10: The project name, developer, or branding information")
    unit_location_map: str = Field(description="Segment 11: Information about the unit's location within the project. Explain clearly around the unit's location in the project in Vietnamese.")
    project_masterplan: str = Field(description="Segment 12: Details about the overall project layout or masterplan. Explain clearly the project layout and the location of the unit in the project in Vietnamese.")
    lifestyle_visuals: str = Field(description="Segment 13: Description of lifestyle amenities or visual elements shown")
    confidence_score: float = Field(description="Confidence level (0.0 to 1.0) for the extraction")
    notes: str = Field(description="Any additional observations or issues with the extraction")

def load_sample_image(sample_file: str) -> Image:
    """
    Load the sample image with bounding boxes.
    Args:
        sample_file: Path to the image file containing labeled sample with bounding boxes
    Returns:
        Image object for multi-modal processing
    """
    try:
        pil_image = PIL.Image.open(sample_file)
        return Image(pil_image)
    except FileNotFoundError:
        raise FileNotFoundError(f"Sample image file {sample_file} not found.")
    except Exception as e:
        raise Exception(f"Error loading sample image {sample_file}: {e}")

def get_image_files(directory: str) -> List[str]:
    """
    Get all image files from a directory.
    Args:
        directory: Path to the directory containing images
    Returns:
        List of image file paths
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    image_files = []
    
    for file_path in Path(directory).rglob('*'):
        if file_path.suffix.lower() in image_extensions:
            image_files.append(str(file_path))
    
    return sorted(image_files)

# Create the Data Extractor agent
data_extractor = AssistantAgent(
    name="DataExtractor",
    model_client=model_client,
    output_content_type=RealEstateProjectData,
    system_message="""
    You are a precise real estate data extraction specialist that converts visual information from property images into structured data.
    
    Your role is to extract data from real estate images
    
    Use the labeled sample image as a template to understand:
    - What fields to extract and where they are located
    - The expected format and units for each field
    - How to identify and categorize different property information
    
    For missing information, use "N/A" or "Not available" rather than leaving fields empty.
    Ensure all monetary values include currency symbols and units where applicable.
    For areas, specify the unit (sqm, sq ft, etc.).
    
    After extraction, say TERMINATE to end the conversation.
    """
)

# Create the team with termination condition
# team = RoundRobinGroupChat(
#     [data_extractor],
#     termination_condition=TextMentionTermination("TERMINATE")
# )

async def process_images_with_team(image_directory: str, sample_image_file: str, output_directory: str = "extracted_data"):
    """
    Process images using the single agent team.
    
    Args:
        image_directory: Directory containing images to process
        sample_image_file: Image file with bounding boxes and labels
        output_directory: Output directory for extracted data JSON files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Load sample image
    try:
        sample_image = load_sample_image(sample_image_file)
        print(f"Loaded sample image: {sample_image_file}")
    except Exception as e:
        print(f"Error loading sample image: {e}")
        return
    
    # Get image files to process
    image_files = get_image_files(image_directory)
    
    if not image_files:
        print(f"No image files found in {image_directory}")
        return
    
    print(f"Found {len(image_files)} images to process")
    print(f"Using sample image: {sample_image_file}")
    print(f"Output directory: {output_directory}")
    
    processed_count = 0
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n--- Processing image {i}/{len(image_files)}: {Path(image_path).name} ---")
        
        try:
            # Load and prepare the image to process
            pil_image = PIL.Image.open(image_path)
            img = Image(pil_image)
            
            # Create multi-modal message with sample image, target image, and instructions
            image_message = MultiModalMessage(
                content=[
                    """Please analyze this real estate image and extract key information about the property.

                    Instructions:
                    1. Examine the image carefully and identify important details about the property
                    2. Provide the extracted data in a structured format matching the defined data models
                    3. Be as specific and detailed as possible while maintaining accuracy""",
                    # sample_image,  # The labeled sample image with bounding boxes
                    img  # The target image to process  
                ],
                source="user"
            )
            
            # Process with the team
            # result = await Console(
            #     team.run_stream(task=image_message),
            #     output_stats=True
            # )

            result = await data_extractor.run(task=image_message)
            
            # Extract the structured data from the result
            extracted_data = None
            for message in reversed(result.messages):
                if hasattr(message, 'content') and isinstance(message.content, RealEstateProjectData):
                    extracted_data = message.content
                    # Update the image_name to match the actual file being processed
                    # extracted_data.image_name = Path(image_path).name
                    print(f"Extracted data: {extracted_data}")
                    break
            
            # Save individual JSON file for this image
            if extracted_data:
                # Create output filename based on image name
                image_name = Path(image_path).stem  # Get filename without extension
                output_file = os.path.join(output_directory, f"{image_name}.json")
                
                # Convert Pydantic model to dictionary and save
                data_dict = extracted_data.model_dump()
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data_dict, f, indent=2, ensure_ascii=False)
                
                print(f"Saved extracted data to: {output_file}")
                processed_count += 1
            else:
                print(f"No structured data extracted for {Path(image_path).name}")
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            continue
    
    # Summary
    if processed_count > 0:
        print(f"\n=== Processing Complete ===")
        print(f"Successfully processed {processed_count} out of {len(image_files)} images")
        print(f"Individual JSON files saved in: {output_directory}")
    else:
        print("No data was extracted successfully.")

# Run the multi-modal data extraction
if __name__ == "__main__":
    # Example usage
    image_dir = "images"  # Directory containing images to process
    sample_image_file = "labelled_sample.png"  # Image file with bounding boxes and labels
    output_dir = "extracted_data" # Output directory for individual JSON files
    
    # Create images directory if it doesn't exist
    os.makedirs(image_dir, exist_ok=True)
    print(f"Images directory: {image_dir}")
    print(f"Sample image file: {sample_image_file}")
    print(f"Output directory for individual JSON files: {output_dir}")
    print("Please ensure the sample image file exists and place your images in the images directory.")
    
    # Uncomment the line below to run the extraction
    asyncio.run(process_images_with_team(image_dir, sample_image_file, output_dir))
