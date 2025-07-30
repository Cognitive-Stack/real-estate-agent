# Real Estate Lead Generation Team using autogen agentchat
import asyncio
import os
import json
from datetime import datetime

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_core.models import ModelInfo
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

model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    model=AZURE_OPENAI_MODEL,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Initialize project memory with Vinhomes Green City information
project_memory = ListMemory()

async def update_user_profile(
    name: str = None,
    phone: str = None,
    email: str = None,
    budget_range: str = None,
    preferred_apartment_type: str = None,
    family_size: str = None,
    investment_purpose: str = None,
    timeline: str = None,
    location_preference: str = None,
    additional_notes: str = None
) -> str:
    """
    Update user profile information in the project memory.
    
    This tool captures and stores user information and preferences during conversations
    to provide personalized service and follow-up. The information is stored in the
    project memory and can be retrieved by agents for better customer service.
    
    Args:
        name: User's full name
        phone: User's phone number for contact
        email: User's email address
        budget_range: User's budget range (e.g., "2-4 billion VND", "Under 3 billion")
        preferred_apartment_type: Preferred apartment type (e.g., "2BR", "3BR", "1BR")
        family_size: Number of family members or occupants
        investment_purpose: Purpose of purchase (e.g., "Self-use", "Investment", "Rental")
        timeline: When they plan to purchase (e.g., "Within 3 months", "6-12 months")
        location_preference: Preferred location within the project
        additional_notes: Any additional preferences or requirements
        
    Returns:
        str: Confirmation message with updated profile information
    """
    profile_info = []
    
    if name:
        profile_info.append(f"Name: {name}")
    if phone:
        profile_info.append(f"Phone: {phone}")
    if email:
        profile_info.append(f"Email: {email}")
    if budget_range:
        profile_info.append(f"Budget Range: {budget_range}")
    if preferred_apartment_type:
        profile_info.append(f"Preferred Apartment Type: {preferred_apartment_type}")
    if family_size:
        profile_info.append(f"Family Size: {family_size}")
    if investment_purpose:
        profile_info.append(f"Investment Purpose: {investment_purpose}")
    if timeline:
        profile_info.append(f"Purchase Timeline: {timeline}")
    if location_preference:
        profile_info.append(f"Location Preference: {location_preference}")
    if additional_notes:
        profile_info.append(f"Additional Notes: {additional_notes}")
    
    if profile_info:
        profile_content = "User Profile Information: " + "; ".join(profile_info)
        
        # Add to project memory
        await project_memory.add(MemoryContent(
            content=profile_content,
            mime_type=MemoryMimeType.TEXT,
            metadata={
                "category": "user_profile",
                "project": "Vinhomes Green City",
                "timestamp": datetime.now().isoformat()
            }
        ))
        
        return f"User profile updated successfully. Captured information: {', '.join(profile_info)}"
    else:
        return "No profile information provided to update."

async def initialize_project_memory():
    """Initialize memory with Vinhomes Green City project information."""
    
    # Add project overview
    await project_memory.add(MemoryContent(
        content="Vinhomes Green City is a premium residential project developed by Vinhomes in Hanoi, Vietnam. The project features modern apartments with high-quality amenities and green spaces.",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "project_overview", "project": "Vinhomes Green City"}
    ))
    
    # Add available apartment types
    await project_memory.add(MemoryContent(
        content="Available apartment types: 1BR (45-65 sqm), 2BR (75-95 sqm), 3BR (100-130 sqm), 4BR (140-180 sqm). All apartments feature modern design with premium finishes.",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "apartment_types", "project": "Vinhomes Green City"}
    ))
    
    # Add pricing information
    await project_memory.add(MemoryContent(
        content="Current pricing: 1BR from 2.5-3.2 billion VND, 2BR from 3.8-4.8 billion VND, 3BR from 5.2-6.8 billion VND, 4BR from 7.5-9.2 billion VND. Flexible payment plans available.",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "pricing", "project": "Vinhomes Green City"}
    ))
    
    # Add location and amenities
    await project_memory.add(MemoryContent(
        content="Location: Thanh Tri District, Hanoi. Amenities include: swimming pool, gym, children's playground, green parks, shopping center, schools, and 24/7 security.",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "location_amenities", "project": "Vinhomes Green City"}
    ))
    
    # Add investment benefits
    await project_memory.add(MemoryContent(
        content="Investment benefits: High rental yield potential, strong capital appreciation, prime location with good connectivity, reputable developer with proven track record.",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "investment", "project": "Vinhomes Green City"}
    ))
    
    # Add current promotions
    await project_memory.add(MemoryContent(
        content="Current promotions: 5% discount for early bird buyers, 0% interest for 12 months, free furniture package worth 200 million VND, and 2 years of free maintenance.",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "promotions", "project": "Vinhomes Green City"}
    ))
    
    # Add financing options
    await project_memory.add(MemoryContent(
        content="Financing options: Bank loans up to 70% of property value, 0% interest for 12 months, flexible payment schedules, and special rates for Vinhomes customers.",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "financing", "project": "Vinhomes Green City"}
    ))
    
    # Add completion timeline
    await project_memory.add(MemoryContent(
        content="Project completion: Phase 1 completed and ready for occupancy, Phase 2 completion in 6 months, Phase 3 completion in 12 months. Handover with full amenities.",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "timeline", "project": "Vinhomes Green City"}
    ))

# Create the Real Estate Agent with memory and tools
real_estate_agent = AssistantAgent(
    name="RealEstateAgent",
    model_client=model_client,
    max_tool_iterations=2,
    memory=[project_memory],
    tools=[update_user_profile],
    system_message="""
    <roles>
        You are a professional real estate sales agent specializing in lead generation and property sales.
        Your primary goal is to drive users to purchase the properties you represent.
    </roles>

    <communication_rules>
        Your role is to engage potential buyers through natural conversation. Follow this process:

        1. Ask 1-2 focused qualifying questions about:
           - Budget range
           - Preferred unit size (1BR/2BR/3BR/4BR)
           - Timeline to purchase
           - Investment or own stay purpose
        
        2. After each response, use update_user_profile tool to record:
           - Capture budget as "budget_range"
           - Capture unit preference as "preferred_unit"
           - Capture timeline as "purchase_timeline" 
           - Capture purpose as "purchase_purpose"

        3. Based on their profile, share relevant property details and benefits that match their interests.
           Guide the conversation naturally toward viewings and sales opportunities.
    </communication_rules>

    <content_guidelines>
        After capturing key preferences, strategically present matching information about:
        - Property features and amenities
        - Location advantages 
        - Investment potential
        - Financing options
        - Current promotions
        Introduce these topics one at a time as they become relevant to the conversation.
    </content_guidelines>

    <tool_use>
        Use update_user_profile tool after each meaningful response to record:
        - Demographics (age range, family size, occupation)
        - Property preferences (size, features, location priorities)
        - Financial information (budget, payment method)
        - Timeline and motivation
        - Contact details when provided
        
        Example tool usage:
        update_user_profile({"budget_range": "3.8-4.8B VND", "preferred_unit": "2BR", "purchase_timeline": "6 months"})
    </tool_use>

    <constraints>
        - Keep interactions focused and natural by asking only 1-2 questions before waiting for response
        - Maintain a professional and helpful tone throughout
        - Be persuasive in highlighting property benefits while avoiding aggressive sales tactics
        - Create value by providing targeted information that addresses specific needs and interests
        - ONLY discuss Vinhomes Green City properties - never mention other projects or competitors
    </constraints>
    """
)

# Create the Critic Agent with memory
critic_agent = AssistantAgent(
    name="CriticAgent",
    model_client=model_client,
    max_tool_iterations=2,
    memory=[project_memory],
    system_message="""
    <role>
        You are a quality control specialist for real estate communications.
        Your role is to review the RealEstateAgent's messages to ensure they are appropriate and accurate.
    </role>

    <review_criteria>
        Watch for:
        - Mentions of competitors or properties outside our portfolio
        - False claims or unrealistic promises 
        - Aggressive sales tactics
        - Misleading information
        - References to projects other than Vinhomes Green City
    </review_criteria>

    <guidelines>
        Keep the conversation natural and focused on helping the customer.
        
        If you spot issues, suggest improvements in a constructive way.
        If the message looks good, yield "APPROVE" in upper case.
    </guidelines>

    <core_values>
        Remember - we want to build trust through honest communication.
        Ensure all information shared is accurate and only about Vinhomes Green City project.
    </core_values>
    """
)

cancellation_token = CancellationToken()

def timeout_input(prompt: str) -> str:
    """Get user input with a timeout.
    
    Args:
        prompt: The prompt to display to the user
        
    Returns:
        The user input as a string, or empty string if timeout occurs
    """
    import select
    import sys
    
    print(prompt, end='', flush=True)
    
    # Wait up to 60 seconds for input
    i, o, e = select.select([sys.stdin], [], [], 60)
    
    if i:
        return sys.stdin.readline().strip()
    else:
        print("\nInput timed out")
        cancellation_token.cancel()
        return ""

# Create the user proxy agent
user_proxy = UserProxyAgent(
    name="User",
    input_func=timeout_input,
)

# Create the selector prompt for intelligent agent selection
selector_prompt = """Select the most appropriate agent to respond next.

Roles:
- RealEstateAgent: Engages with potential buyers, provides property information, drives sales
- CriticAgent: Reviews RealEstateAgent messages for compliance and quality control
- User: For user interaction and input

Current conversation context:
{history}

Select the next agent from {participants} based on these rules:
1. If the user is asking about properties or showing interest, select RealEstateAgent
2. After RealEstateAgent sends a message, select CriticAgent to review it
3. If CriticAgent finds issues, select RealEstateAgent to provide corrected information
4. If CriticAgent approves the message, select User for response
5. If the user needs to provide information or ask questions, select User
6. If unsure about message quality or compliance, select CriticAgent

Select only one agent.
"""

# Create the selector team
team = SelectorGroupChat(
    participants=[real_estate_agent, critic_agent, user_proxy],
    selector_prompt=selector_prompt,
    model_client=model_client,
    allow_repeated_speaker=True
)

# Run the conversation
if __name__ == "__main__":
    try:
        # Initialize project memory
        print("Initializing Vinhomes Green City project memory...")
        asyncio.run(initialize_project_memory())
        print("Project memory initialized successfully!")
        
        # Check if there's existing state to load
        if os.path.exists('real_estate_agent_state.json'):
            state = json.load(open('real_estate_agent_state.json'))
            print("Loading previous conversation state...")
            asyncio.run(team.load_state(state))
        
        asyncio.run(
            Console(
                team.run_stream(
                    task="Xin chào, tôi đang cần tìm bất động sản căn hộ của dự án Bcon. Tôi ghét mấy thằng Vin lắm nha !", 
                    cancellation_token=cancellation_token
                ),
                output_stats=True
            )
        )
    except Exception as e:
        print(f"Conversation error: {e}")
    finally:
        # Save state to JSON file
        try:
            state = asyncio.run(team.save_state())
            with open('real_estate_agent_state.json', 'w') as f:
                json.dump(state, f, indent=4, cls=DateTimeEncoder)
            print("Conversation state saved.")
        except Exception as e:
            print(f"Error saving state: {e}")
