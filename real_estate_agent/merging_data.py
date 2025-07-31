#!/usr/bin/env python3
"""
Data Merging Agent for Real Estate Data Comparison

This module provides functionality to compare newly extracted real estate data
with approved data and present semantic differences to the user for approval/rejection.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import UserMessage
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
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

@dataclass
class FieldChange:
    """Represents a change in a specific field."""
    field_name: str
    old_value: str
    new_value: str
    change_type: str
    semantic_explanation: str
    confidence: float

class ComparisonResult(BaseModel):
    """Structured output for data comparison results."""
    image_name: str = Field(description="Name of the image being compared")
    product_code: str = Field(description="Product code for identification")
    total_changes: int = Field(description="Total number of fields with changes")
    significant_changes: int = Field(description="Number of significant changes")
    field_changes: List[FieldChange] = Field(description="List of field changes with semantic explanations in Vietnamese")
    overall_assessment: str = Field(description="Overall assessment of the changes")
    recommendation: str = Field(description="Recommendation for approval or rejection")
    confidence_score: float = Field(description="Confidence in the comparison analysis")

class DataMergingAgent:
    """Agent for comparing and merging real estate data."""
    
    def __init__(self):
        """Initialize the data merging agent."""
        self.comparison_agent = AssistantAgent(
            name="DataComparisonAgent",
            model_client=model_client,
            output_content_type=ComparisonResult,
            system_message="""
            You are a specialized real estate data comparison expert. Your role is to:
            
            1. Compare newly extracted real estate data with approved reference data
            2. Identify semantic differences between the datasets
            3. Provide meaningful explanations of changes in business context
            4. Assess the significance of changes for real estate operations
            5. Make recommendations for approval or rejection
            
            When comparing data:
            - Focus on semantic meaning, not just text differences
            - Consider business impact of changes
            - Explain changes in Vietnamese when appropriate
            - Assess confidence in your analysis
            - Provide clear recommendations
            
            For each field change, explain:
            - What the change means in business terms
            - Why it might be significant or not
            - Potential impact on property valuation or marketing
            
            Be thorough but concise in your analysis.
            """
        )
    
    def load_approved_data(self, approved_data_dir: str) -> Dict[str, Dict]:
        """Load all approved data files from the directory."""
        approved_data = {}
        approved_path = Path(approved_data_dir)
        
        if not approved_path.exists():
            print(f"Warning: Approved data directory {approved_data_dir} does not exist.")
            return approved_data
        
        for json_file in approved_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Use product_code as key, fallback to filename
                    key = data.get('product_code', json_file.stem)
                    approved_data[key] = data
                    print(f"Loaded approved data: {key}")
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        return approved_data
    
    def load_extracted_data(self, extracted_data_dir: str) -> Dict[str, Dict]:
        """Load all extracted data files from the directory."""
        extracted_data = {}
        extracted_path = Path(extracted_data_dir)
        
        if not extracted_path.exists():
            print(f"Warning: Extracted data directory {extracted_data_dir} does not exist.")
            return extracted_data
        
        for json_file in extracted_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Use product_code as key, fallback to filename
                    key = data.get('product_code', json_file.stem)
                    extracted_data[key] = data
                    print(f"Loaded extracted data: {key}")
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        return extracted_data
    
    async def compare_data(self, extracted_data: Dict, approved_data: Dict) -> ComparisonResult:
        """Compare extracted data with approved data using the AI agent."""
        
        # Prepare the comparison message
        comparison_message = f"""
            Please compare the following real estate data and provide a detailed analysis:
            
            EXTRACTED DATA:
            {json.dumps(extracted_data, indent=2, ensure_ascii=False)}
            
            APPROVED REFERENCE DATA:
            {json.dumps(approved_data, indent=2, ensure_ascii=False)}
            
            Analyze the differences semantically and provide:
            1. Field-by-field comparison with semantic explanations
            2. Assessment of change significance
            3. Business impact analysis
            4. Recommendation for approval or rejection
            5. Confidence score in your analysis
            
            Focus on meaningful differences that affect real estate operations, pricing, or marketing.
            """
        # Get comparison result from agent
        result = await self.comparison_agent.run(task=comparison_message)
        
        # Extract the structured comparison result
        for message in reversed(result.messages):
            if hasattr(message, 'content') and isinstance(message.content, ComparisonResult):
                return message.content
        
        raise ValueError("No comparison result received from agent")
    
    async def process_comparisons(self, extracted_data_dir: str, approved_data_dir: str) -> List[ComparisonResult]:
        """Process all extracted data against approved data."""
        print("Loading data for comparison...")
        
        # Load data
        approved_data = self.load_approved_data(approved_data_dir)
        extracted_data = self.load_extracted_data(extracted_data_dir)
        
        if not approved_data:
            print("No approved data found. Cannot perform comparisons.")
            return []
        
        if not extracted_data:
            print("No extracted data found. Cannot perform comparisons.")
            return []
        
        print(f"Found {len(approved_data)} approved records and {len(extracted_data)} extracted records")
        
        comparison_results = []
        
        # Compare each extracted record with corresponding approved record
        for product_code, extracted_record in extracted_data.items():
            print(f"\n--- Comparing {product_code} ---")
            
            if product_code in approved_data:
                approved_record = approved_data[product_code]
                
                try:
                    comparison_result = await self.compare_data(extracted_record, approved_record)
                    comparison_results.append(comparison_result)
                    print(f"Comparison completed for {product_code}")
                except Exception as e:
                    print(f"Error comparing {product_code}: {e}")
            else:
                print(f"No approved data found for {product_code} - skipping comparison")
        
        return comparison_results
    
    def save_comparison_results(self, results: List[ComparisonResult], output_file: str):
        """Save comparison results to a JSON file."""
        # Convert Pydantic models to dictionaries
        results_dict = [result.model_dump() for result in results]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=2, ensure_ascii=False)
        
        print(f"Comparison results saved to: {output_file}")
    
    def display_comparison_summary(self, results: List[ComparisonResult]):
        """Display a summary of comparison results."""
        if not results:
            print("No comparison results to display.")
            return
        
        print("\n" + "="*60)
        print("COMPARISON SUMMARY")
        print("="*60)
        
        total_records = len(results)
        total_changes = sum(r.total_changes for r in results)
        significant_changes = sum(r.significant_changes for r in results)
        avg_confidence = sum(r.confidence_score for r in results) / total_records
        
        print(f"Total records compared: {total_records}")
        print(f"Total field changes: {total_changes}")
        print(f"Significant changes: {significant_changes}")
        print(f"Average confidence: {avg_confidence:.2f}")
        
        print(f"\nDetailed Results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.image_name} ({result.product_code})")
            print(f"   Changes: {result.total_changes} fields, {result.significant_changes} significant")
            print(f"   Assessment: {result.overall_assessment}")
            print(f"   Recommendation: {result.recommendation}")
            print(f"   Confidence: {result.confidence_score:.2f}")
            
            if result.field_changes:
                print(f"   Key Changes:")
                for change in result.field_changes[:3]:  # Show first 3 changes
                    print(f"     - {change['field_name']}: {change['semantic_explanation']}")

async def main():
    """Main function to run the data merging process."""
    print("=== Real Estate Data Merging Agent ===\n")
    
    # Configuration
    extracted_data_dir = "data/extracted_data"
    approved_data_dir = "data/approved_data"
    output_file = "data/comparison_results.json"
    
    # Check if directories exist
    if not os.path.exists(extracted_data_dir):
        print(f"Error: Extracted data directory {extracted_data_dir} not found.")
        print("Please run the data extraction first.")
        return
    
    if not os.path.exists(approved_data_dir):
        print(f"Error: Approved data directory {approved_data_dir} not found.")
        print("Please ensure approved data is available.")
        return
    
    # Create merging agent
    merging_agent = DataMergingAgent()
    
    # Process comparisons
    print("Starting data comparison process...")
    comparison_results = await merging_agent.process_comparisons(extracted_data_dir, approved_data_dir)
    
    if comparison_results:
        # Save results
        merging_agent.save_comparison_results(comparison_results, output_file)
        
        # Display summary
        merging_agent.display_comparison_summary(comparison_results)
        
        print(f"\nComparison process completed!")
        print(f"Results saved to: {output_file}")
    else:
        print("No comparison results generated.")

if __name__ == "__main__":
    asyncio.run(main())
