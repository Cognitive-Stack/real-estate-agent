"""
Simple Real Estate Chat Agent using AutoGen

This module implements a conversational AI agent specialized in real estate
using Microsoft's AutoGen framework.
"""

import os
import sys
import asyncio
import logging
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from tools_v1 import REAL_ESTATE_TOOLS, get_global_preference_manager

# Import our custom logging configuration
import sys
sys.path.append('..')
try:
    from logging_config import setup_advanced_logging, add_autogen_highlights, suppress_mongodb_logs
except ImportError:
    # Fallback to basic logging if custom config is not available
    def setup_advanced_logging(log_level="INFO", enable_file_logging=True):
        logging.basicConfig(level=getattr(logging, log_level.upper()))
    def add_autogen_highlights():
        pass
    def suppress_mongodb_logs():
        pass

# Load environment variables
load_dotenv()


def setup_logging(level: str = "INFO", enable_file_logging: bool = True) -> None:
    """
    Setup logging configuration for AutoGen and the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        enable_file_logging: Whether to enable file logging
    """
    try:
        # Use advanced logging configuration
        # setup_advanced_logging(level, enable_file_logging)
        add_autogen_highlights()
        # Explicitly suppress MongoDB logs again to be sure
        suppress_mongodb_logs()
    except Exception as e:
        # Fallback to basic logging
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('real_estate_agent.log') if enable_file_logging else logging.NullHandler()
            ]
        )
        print(f"⚠️  Using basic logging configuration due to: {e}")
    
    # Configure specific loggers
    loggers_config = {
        "autogen": level,
        "openai": "WARNING",  # Reduce API noise
        "httpx": "WARNING",   # Reduce HTTP request noise
        "real_estate_agent": level
    }
    
    for logger_name, log_level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level.upper()))


class RealEstateChatAgent:
    """A simple real estate chat agent using AutoGen."""
    
    def __init__(self, api_key: Optional[str] = None, log_level: str = "INFO", enable_file_logging: bool = True):
        """
        Initialize the real estate chat agent.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY in environment.
            log_level: Logging level for AutoGen and application logs (DEBUG, INFO, WARNING, ERROR)
            enable_file_logging: Whether to enable file logging
        """
        # Setup logging first
        setup_logging(log_level, enable_file_logging)
        self.logger = logging.getLogger("real_estate_agent.chat_agent")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model_name = os.getenv("MODEL_NAME", "gpt-4o")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        self.logger.info(f"🚀 Initializing Real Estate Chat Agent with model: {self.model_name}")
        
        
        # Initialize the model client, memory, and preference manager
        self.model_client = self._create_model_client()
        self.memory = self._create_memory()
        self.preference_manager = get_global_preference_manager()
        
        # Load user preferences from JSON into memory
        asyncio.create_task(self._load_user_preferences_to_memory())
        
        # Load mock data into memory
        asyncio.create_task(self._load_mock_data_to_memory())
        
        self.agent = self._create_agent()
    
    def _create_model_client(self) -> OpenAIChatCompletionClient:
        """Create and configure the OpenAI model client."""
        self.logger.info(f"Creating OpenAI model client with model: {self.model_name}, temperature: {self.temperature}")
        return OpenAIChatCompletionClient(
            model=self.model_name,
            api_key=self.api_key,
            temperature=self.temperature,
        )
    
    def _create_memory(self) -> ListMemory:
        """Create and configure the ListMemory for the agent."""
        self.logger.info("Creating ListMemory for agent memory management")
        memory = ListMemory()
        
        # Add some default real estate preferences/knowledge to memory
        # These will be available to the agent to provide consistent context
        self.logger.info("Adding default real estate knowledge to memory")
        return memory
    
    async def _load_user_preferences_to_memory(self) -> None:
        """Load user preferences from JSON file into memory."""
        try:
            # Get preferences from JSON file
            preferences = self.preference_manager.get_preferences()
            
            # Load user profile into memory
            user_profile = preferences.get("user_profile", {})
            if user_profile.get("name") or any(user_profile.values()):
                memory_content = MemoryContent(
                    content=f"User Profile: {user_profile}",
                    mime_type=MemoryMimeType.TEXT,
                    metadata={"category": "user_profile", "type": "user_preference", "priority": "high"}
                )
                await self.memory.add(memory_content)
                self.logger.info("User profile loaded from JSON file into memory")
            
            # Load property preferences into memory
            property_prefs = preferences.get("property_preferences", {})
            if any(v for v in property_prefs.values() if v not in [None, [], ""]):
                memory_content = MemoryContent(
                    content=f"Property Preferences: {property_prefs}",
                    mime_type=MemoryMimeType.TEXT,
                    metadata={"category": "property_preferences", "type": "user_preference", "priority": "high"}
                )
                await self.memory.add(memory_content)
                self.logger.info("Property preferences loaded from JSON file into memory")
            
            # Load recent conversation context if available
            context = preferences.get("conversation_context", {})
            if context.get("recent_interests"):
                memory_content = MemoryContent(
                    content=f"Recent Interests: {context['recent_interests']}",
                    mime_type=MemoryMimeType.TEXT,
                    metadata={"category": "conversation_context", "type": "user_preference"}
                )
                await self.memory.add(memory_content)
                self.logger.info("Conversation context loaded from JSON file into memory")

        except Exception as e:
            self.logger.error(f"Error loading user preferences from JSON file: {e}")
            # Fallback to loading default preferences if JSON loading fails
            await self._load_default_user_preferences()
    
    async def _load_default_user_preferences(self) -> None:
        """Load default user preferences if no JSON file exists."""
        try:
            # This will create the default JSON structure
            default_profile = { 
                "name": "Lê Việt Thắng",
                "phone_number": "+1234567890",
                "age": 25,
            }
            
            default_property_prefs = {
                "property_type": ["apartment"],
                "locations": ["Quận 9, Hồ Chí Minh"],
                "budget_max": 2000000000,  # 2 tỷ VND
                "currency": "VND",
                "bedrooms_min": 2,
                "must_have_amenities": ["balcony"],
                "nice_to_have_amenities": ["nearby_schools", "nearby_parks"]
            }

            # Update the JSON file with defaults
            self.preference_manager.update_user_profile(**default_profile)
            self.preference_manager.update_property_preferences(**default_property_prefs)

            # Load into memory
            memory_content = MemoryContent(
                content=f"User Profile: {default_profile}",
                mime_type=MemoryMimeType.TEXT,
                metadata={"category": "user_profile", "type": "user_preference", "priority": "high"}
            )
            await self.memory.add(memory_content)

            memory_content = MemoryContent(
                content=f"Property Preferences: {default_property_prefs}",
                mime_type=MemoryMimeType.TEXT,
                metadata={"category": "property_preferences", "type": "user_preference", "priority": "high"}
            )
            await self.memory.add(memory_content)
            
            self.logger.info("Default user preferences created and loaded into memory")

        except Exception as e:
            self.logger.error(f"Error loading default user preferences: {e}")
    
    async def _load_mock_data_to_memory(self) -> None:
        """Load mock property groups and properties data into memory."""
        try:
            import json
            
            # Load mock property groups
            property_groups_path = Path(__file__).parent.parent / "mock_data" / "mock_property_group_schema_data.json"
            if property_groups_path.exists():
                with open(property_groups_path, 'r', encoding='utf-8') as f:
                    property_groups = json.load(f)
                
                # Add property groups to memory
                for i, group in enumerate(property_groups[:5]):  # Load first 5 groups to avoid overwhelming memory
                    group_summary = {
                        "type": "property_group",
                        "index": i,
                        "location": self._extract_location_from_group(group),
                        "amenities": self._extract_amenities_from_group(group),
                        "developer": self._extract_developer_from_group(group),
                        "project_name": self._extract_project_name_from_group(group)
                    }
                    
                    memory_content = MemoryContent(
                        content=f"Property Group {i+1}: {json.dumps(group_summary, ensure_ascii=False)}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"category": "property_groups", "type": "mock_data", "priority": "medium", "group_index": i}
                    )
                    await self.memory.add(memory_content)
                
                self.logger.info(f"Loaded {min(5, len(property_groups))} property groups into memory")
            
            # Load mock properties
            properties_path = Path(__file__).parent.parent / "mock_data" / "mock_property_schema_data.json"
            if properties_path.exists():
                with open(properties_path, 'r', encoding='utf-8') as f:
                    properties = json.load(f)
                
                # Add properties to memory
                for i, property_data in enumerate(properties[:10]):  # Load first 10 properties
                    property_summary = {
                        "type": "property",
                        "unitId": property_data.get("unitId"),
                        "groupIds": property_data.get("groupIds", []),
                        "description": property_data.get("description", ""),
                        "bedrooms": self._extract_bedrooms_from_property(property_data),
                        "bathrooms": self._extract_bathrooms_from_property(property_data),
                        "area": self._extract_area_from_property(property_data),
                        "price": self._extract_price_from_property(property_data),
                        "has_balcony": self._extract_balcony_from_property(property_data),
                        "furnished": self._extract_furnished_from_property(property_data)
                    }
                    
                    memory_content = MemoryContent(
                        content=f"Property {property_data.get('unitId', i+1)}: {json.dumps(property_summary, ensure_ascii=False)}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"category": "properties", "type": "mock_data", "priority": "medium", "property_index": i}
                    )
                    await self.memory.add(memory_content)
                
                self.logger.info(f"Loaded {min(10, len(properties))} properties into memory")
            
            # Add summary information about available mock data
            summary_content = MemoryContent(
                content="Mock Data Summary: The agent has access to property groups and individual properties data including locations, amenities, pricing, and detailed specifications. This data can be used to provide realistic property recommendations and comparisons.",
                mime_type=MemoryMimeType.TEXT,
                metadata={"category": "mock_data_summary", "type": "system_info", "priority": "high"}
            )
            await self.memory.add(summary_content)
            
        except Exception as e:
            self.logger.error(f"Error loading mock data into memory: {e}")
    
    def _extract_location_from_group(self, group: dict) -> str:
        """Extract location information from property group data."""
        try:
            location_data = group.get("location_and_surrounding_amenities", {}).get("value", [])
            for item in location_data:
                if item.get("key") == "exact_location_on_map":
                    coords = item.get("value", [])
                    lat = next((c["value"] for c in coords if c.get("key") == "latitude"), None)
                    lng = next((c["value"] for c in coords if c.get("key") == "longitude"), None)
                    if lat and lng:
                        return f"Coordinates: {lat}, {lng}"
            return "Location data available"
        except:
            return "Unknown location"
    
    def _extract_amenities_from_group(self, group: dict) -> list:
        """Extract amenities from property group data."""
        try:
            amenities = []
            location_data = group.get("location_and_surrounding_amenities", {}).get("value", [])
            for item in location_data:
                if item.get("key") == "surrounding_amenities":
                    amenity_list = item.get("value", [])
                    for amenity in amenity_list:
                        amenities.append(amenity.get("label", amenity.get("key", "")))
            return amenities[:5]  # Return first 5 amenities
        except:
            return []
    
    def _extract_developer_from_group(self, group: dict) -> str:
        """Extract developer information from property group data."""
        try:
            developer_data = group.get("developer_and_contractor", {}).get("value", [])
            for item in developer_data:
                if item.get("key") == "developer_name":
                    return item.get("value", "Unknown developer")
            return "Developer information available"
        except:
            return "Unknown developer"
    
    def _extract_project_name_from_group(self, group: dict) -> str:
        """Extract project name from property group data."""
        try:
            project_data = group.get("project_information", {}).get("value", [])
            for item in project_data:
                if item.get("key") == "project_name":
                    return item.get("value", "Unknown project")
            return "Project information available"
        except:
            return "Unknown project"
    
    def _extract_bedrooms_from_property(self, property_data: dict) -> int:
        """Extract number of bedrooms from property data."""
        try:
            physical_features = property_data.get("data", {}).get("physical_features", {}).get("value", [])
            for feature in physical_features:
                if feature.get("key") == "number_of_bedrooms":
                    return feature.get("value", 0)
            return 0
        except:
            return 0
    
    def _extract_bathrooms_from_property(self, property_data: dict) -> int:
        """Extract number of bathrooms from property data."""
        try:
            physical_features = property_data.get("data", {}).get("physical_features", {}).get("value", [])
            for feature in physical_features:
                if feature.get("key") == "number_of_bathrooms":
                    return feature.get("value", 0)
            return 0
        except:
            return 0
    
    def _extract_area_from_property(self, property_data: dict) -> float:
        """Extract area from property data."""
        try:
            physical_features = property_data.get("data", {}).get("physical_features", {}).get("value", [])
            for feature in physical_features:
                if feature.get("key") == "gross_floor_area":
                    return feature.get("value", 0.0)
            return 0.0
        except:
            return 0.0
    
    def _extract_price_from_property(self, property_data: dict) -> dict:
        """Extract price information from property data."""
        try:
            pricing_data = property_data.get("data", {}).get("pricing_and_financial_information", {}).get("value", [])
            for item in pricing_data:
                if item.get("key") == "listing_price":
                    return {
                        "amount": item.get("value", 0),
                        "currency": item.get("unit", "VND")
                    }
            return {"amount": 0, "currency": "VND"}
        except:
            return {"amount": 0, "currency": "VND"}
    
    def _extract_balcony_from_property(self, property_data: dict) -> bool:
        """Extract balcony information from property data."""
        try:
            physical_features = property_data.get("data", {}).get("physical_features", {}).get("value", [])
            for feature in physical_features:
                if feature.get("key") == "has_balcony_or_logia":
                    return feature.get("value", False)
            return False
        except:
            return False
    
    def _extract_furnished_from_property(self, property_data: dict) -> bool:
        """Extract furnished status from property data."""
        try:
            amenities_data = property_data.get("data", {}).get("amenities_and_features", {}).get("value", [])
            for item in amenities_data:
                if "furniture" in item.get("key", "").lower() or "furnished" in item.get("key", "").lower():
                    return item.get("value", False)
            return False
        except:
            return False
    
    async def add_user_preference(self, preference: str, category: str = "general") -> None:
        """
        Add a user preference to memory.
        
        Args:
            preference: The user preference to store
            category: Category of the preference (e.g., 'location', 'budget', 'property_type')
        """
        try:
            memory_content = MemoryContent(
                content=preference,
                mime_type=MemoryMimeType.TEXT,
                metadata={"category": category, "type": "user_preference"}
            )
            await self.memory.add(memory_content)
            self.logger.info(f"Added user preference to memory: {preference}")

        except Exception as e:
            self.logger.error(f"Error adding user preference to memory: {e}")
    
    async def update_user_preference(self, preference_key: str, new_value: str, category: str = "general") -> None:
        """
        Update a specific user preference.
        
        Args:
            preference_key: The key of the preference to update (e.g., 'budget', 'location')
            new_value: The new value for the preference
            category: Category of the preference
        """
        try:
            # Add the updated preference
            preference_text = f"Updated {preference_key}: {new_value}"
            await self.add_user_preference(preference_text, category)
            self.logger.info(f"Updated user preference {preference_key} to: {new_value}")
        except Exception as e:
            self.logger.error(f"Error updating user preference: {e}")
    
    async def get_user_preferences(self) -> dict:
        """
        Retrieve all user preferences from memory.
        
        Returns:
            Dictionary containing user preferences
        """
        try:
            memories = await self.memory.query("")
            preferences = {}
            
            for memory in memories:
                metadata = memory.metadata or {}
                if metadata.get("type") == "user_preference":
                    category = metadata.get("category", "general")
                    if category not in preferences:
                        preferences[category] = []
                    preferences[category].append(memory.content)
            
            return preferences
        except Exception as e:
            self.logger.error(f"Error retrieving user preferences: {e}")
            return {}
    
    async def add_conversation_context(self, context: str, context_type: str = "conversation") -> None:
        """
        Add conversation context to memory.
        
        Args:
            context: The context to store
            context_type: Type of context (e.g., 'property_search', 'market_question', 'investment_query')
        """
        try:
            memory_content = MemoryContent(
                content=context,
                mime_type=MemoryMimeType.TEXT,
                metadata={"type": context_type, "category": "conversation_context"}
            )
            await self.memory.add(memory_content)
            self.logger.info(f"Added conversation context to memory: {context[:50]}...")
        except Exception as e:
            self.logger.error(f"Error adding conversation context to memory: {e}")
    
    async def clear_memory(self) -> None:
        """Clear all memories from the agent."""
        try:
            await self.memory.clear()
            self.logger.info("Agent memory cleared successfully")
        except Exception as e:
            self.logger.error(f"Error clearing memory: {e}")
    
    async def query_memory(self, query: str) -> list:
        """
        Query the memory for relevant information.
        
        Args:
            query: The query string to search for relevant memories
            
        Returns:
            List of relevant memory contents
        """
        try:
            results = await self.memory.query(query)
            self.logger.info(f"Memory query returned {len(results)} results for: {query}")
            return results
        except Exception as e:
            self.logger.error(f"Error querying memory: {e}")
            return []
    
    def _create_agent(self) -> AssistantAgent:
        """Create and configure the AutoGen conversable agent."""
        
        self.logger.info("Creating AutoGen AssistantAgent with real estate tools and memory")
        
        # System message defining the agent's role and capabilities
        system_message = f"""
        You are a knowledgeable and helpful real estate assistant with access to user preferences and conversation history through memory. Your role is to:
        
        1. Help users with real estate-related questions
        2. Explain real estate processes, terminology, and market trends
        3. Assist with property valuations and market analysis 
        4. Offer guidance on real estate investments
        5. Help with understanding legal aspects of real estate transactions
        6. Search properties using function calls ONLY when users ask about specific properties or want to search the database
        7. Remember user preferences and conversation context to provide personalized assistance
        8. Update and manage user preferences automatically based on conversation context
        
        IMPORTANT - User Preference Management:
        - You have access to user preference management functions to update user profile and property preferences
        - When users mention their preferences (budget, location, property type, amenities, etc.), AUTOMATICALLY call the appropriate preference update functions
        - Use update_user_profile() when users mention personal information (name, phone, email, age)
        - Use update_property_preferences() when users mention property preferences (budget, location, property type, amenities, etc.)
        - Use update_recent_interests() to track topics and properties users show interest in
        - Use add_search_to_history() to track property searches performed
        - Call get_user_preferences() to retrieve current preferences when needed for personalized responses
        
        IMPORTANT - User Preference Usage:
        - ALWAYS check if user preferences are available in memory before responding
        - Use stored user preferences (budget, location, property type, amenities, etc.) to personalize your responses
        - When suggesting properties or giving advice, consider the user's stated preferences from memory
        - If the user hasn't specified preferences for a particular aspect, you may ask clarifying questions
        - Adapt your recommendations based on the user's profile (age, budget, location preferences, etc.)
        
        IMPORTANT - When to use function calls:
        - ONLY use property/project search functions when users explicitly ask to search for specific properties, contractors, developers, locations, or other database information
        - ALWAYS use preference management functions when users mention preferences, personal info, or show interest in specific topics
        - DO NOT use property search functions for: greetings, general questions, explanations, advice, market trends, educational content, or casual conversation
        - Examples that DO NOT need property search: "hello", "what is a mortgage?", "how does real estate work?", "give me investment advice"
        - Examples that DO need property search: "find properties in Bangkok", "search for contractors", "show me developers", "look for apartments under $500k"
        - Examples that need preference updates: "I'm looking for a 2-bedroom apartment", "My budget is 3 million", "I prefer locations near schools"
        
        PROPERTY SEARCH BEST PRACTICES:
        - When users specify "2-bedroom", use number_of_bedrooms=2 (exact match)
        - For budget "under 3 billion VND", use max_price=3000000000
        - For budget "2-4 billion VND", use min_price=2000000000, max_price=4000000000
        - For size "at least 80 sqm", use min_area=80.0
        - For size "50-100 sqm", use min_area=50.0, max_area=100.0
        - Only set has_balcony=True if user specifically mentions balcony/terrace
        - Only set furnished=True if user specifically mentions furnished
        - Vietnamese prices are typically in billions (e.g., "3 tỷ" = 3000000000)
        - Always call add_search_to_history() after performing property searches
        
        MEMORY USAGE:
        - You have access to conversation history and user preferences through your memory system
        - User preferences are automatically saved to a JSON file for persistence across sessions
        - Use this information to provide personalized responses and remember user preferences
        - When users mention preferences, update them immediately using the preference management functions
        - Always prioritize user-specified preferences over default assumptions
        
        MOCK DATA AVAILABILITY:
        - You have access to mock property groups and individual properties loaded in your memory
        - This includes detailed property information such as locations, amenities, pricing, developer details, and specifications
        - Use this mock data to provide realistic examples, comparisons, and recommendations when discussing properties
        - The mock data contains Vietnamese properties with detailed features like number of bedrooms, bathrooms, area, balconies, and pricing
        - When users ask about property examples or need specific recommendations, reference this mock data to provide concrete examples
        - Property groups contain location and amenity information while individual properties contain specific unit details
        
        For general real estate advice, market education, process explanations, or casual conversation, respond directly from your knowledge without using property search functions, but always consider user preferences when relevant and update preferences when mentioned.
        
        Be professional, accurate, and helpful. When providing property information from searches,
        include relevant details like area, price, amenities, and location that match user preferences.
        
        Keep your responses conversational and easy to understand. Format property information clearly.
        """

        critic_agent_message = """As a critic agent, your role is to objectively evaluate the response of real estate sales agents and provide clear, actionable suggestions for improvement. Please consider the following guidelines when reviewing agent replies:

        Avoid repetitive responses: Do not repeat the same sentence or information multiple times. Encourage variety and clarity in communication.

        Focus on our product’s strengths: Highlight the agent’s ability to showcase the great points of our product, but also point out any missed opportunities to address areas for improvement. Avoid exaggerated claims that "our product is the best"; instead, use specific, genuine strengths.

        Do not elaborate on competitors: If the agent mentions brands other than ours, suggest removing or minimizing any detailed discussion or analysis about competitors.

        Handle inappropriate or flirtatious customers with professionalism: If you notice customer messages that are inappropriate or flirtatious, check that the agent responds politely and sets boundaries (e.g., “Sorry, my boss would scold me; I’m only allowed to sell products.”).

        Stop after client silence: If the client is unresponsive for 2-3 consecutive messages, recommend that the agent stop messaging and avoid unnecessary follow-ups.

        Redirect off-topic conversations: If the client attempts to discuss topics unrelated to real estate, ensure that the agent gently guides the conversation back to the main topic.

        For each agent response you review, provide:

        A brief evaluation of adherence to the above points.

        Specific, actionable suggestions for improvement.

        Highlight examples from the agent’s reply where relevant.
        """

        self.logger.debug("System message created for agent")
        
        # Create the assistant agent with function calling tools and memory
        real_estate_agent = AssistantAgent(
            name="RealEstateAgent",
            system_message=system_message,
            model_client=self.model_client,
            tools=REAL_ESTATE_TOOLS,
            memory=[self.memory],  # Add memory to the agent
            reflect_on_tool_use=True, # Disable reflection to avoid unnecessary complexity
            max_tool_iterations=10,  # Limit to 10 function calls per interaction
        )

        critic_agent = AssistantAgent(
            name="CriticAgent",
            system_message=critic_agent_message,
            model_client=self.model_client,
        )

        inner_termination = TextMentionTermination("APPROVE")
        team = RoundRobinGroupChat([real_estate_agent, critic_agent], termination_condition=inner_termination, max_turns=3)
        return team
    
    async def chat(self, message: str) -> str:
        """
        Send a message to the agent and get a response using streaming.
        
        Args:
            message: The user's message/question
            
        Returns:
            The agent's response
        """
        try:
            self.logger.info(f"User message received: {message}")
            
            # Check if the message contains user preferences and add them to memory
            await self._process_user_preferences(message)
            
            # Add conversation context to memory
            await self.add_conversation_context(f"User asked: {message}")
            
            # Use the Console to stream all messages
            result = await Console(self.agent.run_stream(task=message))
            
            # Extract the final response from the result
            final_response = result.messages[-1].content if result.messages else "No response generated."
            
            # Add the agent's response to conversation context
            await self.add_conversation_context(f"Agent responded: {final_response}", "agent_response")
            
            self.logger.info(f"Agent response completed: {final_response[:100]}...")
            return final_response
                
        except Exception as e:
            self.logger.error(f"Error in chat method: {str(e)}", exc_info=True)
            return f"An error occurred: {str(e)}"
    
    async def _process_user_preferences(self, message: str) -> None:
        """
        Process user message to extract and store preferences.
        
        Args:
            message: The user's message to analyze for preferences
        """
        # Simple keyword-based preference detection
        # In a production system, you might use NLP to better extract preferences
        message_lower = message.lower()
        
        # Budget preferences - improved detection
        budget_keywords = ['budget', 'price', 'cost', 'afford', '$', 'baht', 'million', 'billion', 'thousand', 'tỷ', 'triệu']
        if any(word in message_lower for word in budget_keywords):
            await self.add_user_preference(f"Budget-related preference mentioned: {message}", "budget")
        
        # Location preferences - expanded
        location_keywords = ['bangkok', 'location', 'area', 'district', 'near', 'close to', 'quận', 'huyện', 'thành phố', 'tp', 'hcm', 'hồ chí minh', 'sài gòn']
        if any(word in message_lower for word in location_keywords):
            await self.add_user_preference(f"Location preference mentioned: {message}", "location")
        
        # Property type preferences - expanded
        property_keywords = ['condo', 'house', 'apartment', 'villa', 'townhouse', 'commercial', 'studio', 'penthouse', 'duplex', 'chung cư', 'căn hộ', 'nhà', 'biệt thự']
        if any(word in message_lower for word in property_keywords):
            await self.add_user_preference(f"Property type preference mentioned: {message}", "property_type")
        
        # Investment preferences
        investment_keywords = ['invest', 'investment', 'roi', 'return', 'yield', 'rental', 'profit', 'đầu tư', 'lợi nhuận']
        if any(word in message_lower for word in investment_keywords):
            await self.add_user_preference(f"Investment preference mentioned: {message}", "investment")
        
        # Amenities preferences
        amenity_keywords = ['pool', 'gym', 'parking', 'balcony', 'garden', 'security', 'elevator', 'school', 'hospital', 'mall', 'mrt', 'bts', 'metro']
        if any(word in message_lower for word in amenity_keywords):
            await self.add_user_preference(f"Amenity preference mentioned: {message}", "amenities")
        
        # Size preferences
        size_keywords = ['bedroom', 'bathroom', 'sqm', 'square meter', 'size', 'big', 'small', 'spacious', 'compact', 'phòng ngủ', 'phòng tắm']
        if any(word in message_lower for word in size_keywords):
            await self.add_user_preference(f"Size preference mentioned: {message}", "size")
    
    async def start_interactive_chat(self):
        """Start an interactive chat session in the terminal."""
        
        while True:
            try:
                user_input = input("💬 You: ").strip()            
                if not user_input:
                    print("Please enter a message or type 'quit' to exit.")
                    continue
                
                print("\n🤖 Agent (streaming): ")
                print("=" * 40)
                response = await self.chat(user_input)
                print("=" * 40)
                print(f"✅ Response completed.\n")
                
            except KeyboardInterrupt:
                self.logger.info("Chat session interrupted by user")
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error in interactive chat: {e}", exc_info=True)
                print(f"❌ Error: {e}")
                print("Please try again or type 'quit' to exit.\n")
    
    
    async def close(self):
        """Close the model client connection and clean up memory."""
        self.logger.info("Closing model client connection and cleaning up memory")
        try:
            await self.memory.close()
        except Exception as e:
            self.logger.error(f"Error closing memory: {e}")
        
        try:
            await self.model_client.close()
        except Exception as e:
            self.logger.error(f"Error closing model client: {e}")


async def main():
    """Main function to run the chat agent."""
    # Setup basic logging before creating the agent
    setup_logging("INFO", enable_file_logging=True)
    logger = logging.getLogger("real_estate_agent.main")
    
    agent = None
    try:
        logger.info("🏠 Starting Real Estate Chat Agent application")
        
        # Create and start the chat agent with DEBUG level for more detailed logs
        agent = RealEstateChatAgent(log_level="DEBUG", enable_file_logging=True)
        await agent.start_interactive_chat()
        
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        print(f"❌ Configuration Error: {e}")
        print("Please make sure to set your OPENAI_API_KEY in the .env file.")
    except Exception as e:
        logger.error(f"Unexpected Error: {e}", exc_info=True)
        print(f"❌ Unexpected Error: {e}")
    finally:
        # Close the model client connection
        if agent:
            await agent.close()
        logger.info("🔚 Application shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
