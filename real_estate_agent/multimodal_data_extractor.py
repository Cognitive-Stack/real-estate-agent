# Multi-Modal Data Extractor using autogen agentchat 0.6.2
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List

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
    output_content_type=RealEstateSegments,
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
                    """Please analyze this target real estate image and extract data according to the labeled sample image provided. 
                    
                    Instructions:
                    1. First, examine the labeled sample image to understand what fields need to be extracted and where they are located
                    2. Then analyze the target image and extract the same types of fields in the same format
                    3. Use the bounding boxes and labels in the sample as a guide for what to look for
                    4. Provide structured data extraction based on the sample format""",
                    sample_image,  # The labeled sample image with bounding boxes
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
                if hasattr(message, 'content') and isinstance(message.content, RealEstateSegments):
                    extracted_data = message.content
                    # Update the image_name to match the actual file being processed
                    extracted_data.image_name = Path(image_path).name
                    print(f"Extracted data: {extracted_data.product_code}, {extracted_data.product_type}, {extracted_data.price_standard}")
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
