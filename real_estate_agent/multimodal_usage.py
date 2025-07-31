#!/usr/bin/env python3
"""
Example usage of the Multi-Modal Data Extractor

This script demonstrates how to use the simplified multi-modal data extractor
to process real estate images and extract structured data using a labeled sample image.
After extraction, it runs a comparison agent to compare with approved data.
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add the current directory to the path so we can import our module
sys.path.append(str(Path(__file__).parent))

from multimodal_data_extractor import process_images_with_team
from merging_data import DataMergingAgent

async def main():
    """Main function to demonstrate the multi-modal data extractor."""
    
    # Configuration
    image_dir = "data/images"
    sample_image_file = "data/labelled_sample.png"  # Image with bounding boxes and labels
    output_dir = "data/extracted_data"  # Directory for individual JSON files
    approved_data_dir = "data/approved_data"  # Directory for approved reference data
    
    print("=== Multi-Modal Real Estate Data Extractor Demo ===\n")
    
    # Check if sample image file exists
    if not os.path.exists(sample_image_file):
        print(f"Sample image file {sample_image_file} not found.")
        print("Please ensure you have a labeled sample image with bounding boxes.")
        print("The sample image should show what real estate segments to extract and where they are located.")
        return
    
    # Check if images directory exists and has images
    if not os.path.exists(image_dir):
        print(f"Creating {image_dir} directory...")
        os.makedirs(image_dir, exist_ok=True)
        print(f"Please add some real estate images to the {image_dir} directory and run this script again.")
        print("Supported formats: JPG, PNG, BMP, TIFF, WebP")
        return
    
    # Check if we have images to process
    from multimodal_data_extractor import get_image_files
    image_files = get_image_files(image_dir)
    
    if not image_files:
        print(f"No image files found in {image_dir} directory.")
        print("Please add some real estate images and run this script again.")
        return
    
    print(f"Found {len(image_files)} images to process:")
    for img_file in image_files:
        print(f"  - {Path(img_file).name}")
    
    print(f"\nUsing sample image: {sample_image_file}")
    print(f"Individual JSON files will be saved to: {output_dir}/")
    
    # Ask for confirmation
    response = input("\nProceed with real estate data extraction? (y/n): ").lower().strip()
    if response not in ['y', 'yes']:
        print("Extraction cancelled.")
        return
    
    print("\nStarting multi-modal real estate data extraction...")
    print("This may take a few minutes depending on the number of images.")
    print("The system will extract 13 real estate segments from each image.")
    print("Each image will generate its own JSON file.\n")
    
    try:
        # Run the extraction
        await process_images_with_team(image_dir, sample_image_file, output_dir)
        
        # Show a preview of the results
        if os.path.exists(output_dir):
            json_files = list(Path(output_dir).glob("*.json"))
            
            if json_files:
                print(f"\n=== Extraction Complete ===")
                print(f"Generated {len(json_files)} JSON files in: {output_dir}")
                
                # Show preview of first few results
                print(f"\nPreview of extracted data:")
                for i, json_file in enumerate(json_files[:3], 1):  # Show first 3 results
                    try:
                        with open(json_file, 'r') as f:
                            result = json.load(f)
                        
                        print(f"\nFile {i}: {json_file.name}")
                        print(f"  Image: {result['image_name']}")
                        print(f"  Confidence: {result['confidence_score']:.2f}")
                        print(f"  Key Real Estate Segments:")
                        print(f"    Product Code: {result['product_code']}")
                        print(f"    Product Type: {result['product_type']}")
                        print(f"    Product Zone: {result['product_zone']}")
                        print(f"    Construction Area: {result['construction_area']}")
                        print(f"    Land Area: {result['land_area']}")
                        print(f"    Direction: {result['direction']}")
                        print(f"    Price Standard: {result['price_standard']}")
                        print(f"    Price Early: {result['price_early']}")
                        print(f"    Price Loan: {result['price_loan']}")
                        print(f"    Project Branding: {result['project_branding']}")
                        print(f"    Unit Location Map: {result['unit_location_map']}")
                        print(f"    Project Masterplan: {result['project_masterplan']}")
                        print(f"    Lifestyle Visuals: {result['lifestyle_visuals']}")
                        if result['notes']:
                            print(f"  Notes: {result['notes']}")
                    
                    except Exception as e:
                        print(f"Error reading {json_file.name}: {e}")
                
                if len(json_files) > 3:
                    print(f"\n... and {len(json_files) - 3} more JSON files")
                
                print(f"\nAll JSON files are available in the '{output_dir}' directory.")
                print("Each file contains the complete extracted data for one image.")
                
                # Check if approved data exists for comparison
                if os.path.exists(approved_data_dir):
                    approved_files = list(Path(approved_data_dir).glob("*.json"))
                    if approved_files:
                        print(f"\n=== Data Comparison Phase ===")
                        print(f"Found {len(approved_files)} approved data files for comparison.")
                        
                        # Ask if user wants to proceed with comparison
                        compare_response = input("\nProceed with data comparison against approved data? (y/n): ").lower().strip()
                        if compare_response in ['y', 'yes']:
                            print("\nStarting data comparison process...")
                            print("This will compare extracted data with approved reference data.")
                            print("The system will provide semantic analysis of differences.\n")
                            
                            # Create merging agent and run comparison
                            merging_agent = DataMergingAgent()
                            comparison_results = await merging_agent.process_comparisons(output_dir, approved_data_dir)
                            
                            if comparison_results:
                                # Save comparison results
                                comparison_output_file = "data/comparison_results.json"
                                merging_agent.save_comparison_results(comparison_results, comparison_output_file)
                                
                                # Display comparison summary
                                merging_agent.display_comparison_summary(comparison_results)
                                
                                print(f"\n=== Comparison Complete ===")
                                print(f"Comparison results saved to: {comparison_output_file}")
                                print("\nReview the comparison results above to make approval/rejection decisions.")
                                print("The system provides semantic analysis of changes and recommendations.")
                            else:
                                print("No comparison results generated.")
                        else:
                            print("Data comparison skipped.")
                    else:
                        print(f"\nNo approved data files found in {approved_data_dir}")
                        print("Skipping data comparison phase.")
                else:
                    print(f"\nApproved data directory {approved_data_dir} not found.")
                    print("Skipping data comparison phase.")
            else:
                print(f"No JSON files were generated in {output_dir}")
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        print("Please check your API key and internet connection.")

if __name__ == "__main__":
    # Check for API key
    # if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
    #     print("Error: Environment variable not set.")
    #     print("Please set your API key:")
    #     print("export OPENAI_API_KEY='your_api_key_here'")
    #     print("or")
    #     print("export GEMINI_API_KEY='your_api_key_here'")
    #     sys.exit(1)
    
    # Run the demo
    asyncio.run(main()) 