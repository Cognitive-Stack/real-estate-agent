"""
Simple Real Estate Chat Agent using AutoGen

This module implements a conversational AI agent specialized in real estate
using Microsoft's AutoGen framework.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from .tools_v1 import REAL_ESTATE_TOOLS, get_global_preference_manager

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

class RealEstateChatAgent:
    """A simple real estate chat agent using AutoGen."""
    
    def __init__(self, api_key: Optional[str] = None, log_level: str = "INFO", enable_file_logging: bool = True):
        """
        Initialize the real estate chat agent.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY in environment.
                    For Azure OpenAI, use AZURE_OPENAI_API_KEY environment variable.
            log_level: Logging level for AutoGen and application logs (DEBUG, INFO, WARNING, ERROR)
            enable_file_logging: Whether to enable file logging
        """
        # Setup logging first
        self.logger = logging.getLogger("real_estate_agent.chat_agent")
        
        # Check for Azure OpenAI configuration first
        azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        # If Azure OpenAI configuration is provided, use it
        if azure_openai_deployment and azure_openai_endpoint and azure_openai_api_key:
            self.logger.info("🚀 Initializing Real Estate Chat Agent with Azure OpenAI")
            self.api_key = azure_openai_api_key
            self.model_name = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
        else:
            # Use standard OpenAI
            self.logger.info("🚀 Initializing Real Estate Chat Agent with OpenAI")
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("API key is required. For OpenAI: Set OPENAI_API_KEY environment variable or pass api_key parameter. For Azure OpenAI: Set AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, and AZURE_OPENAI_ENDPOINT environment variables.")
            self.model_name = os.getenv("MODEL_NAME", "gpt-4o")
        
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        self.logger.info(f"Using model: {self.model_name}")
        
        
        # Initialize the model client, memory, and preference manager
        self.model_client = self._create_model_client()
        self.memory = self._create_memory()
        self.preference_manager = get_global_preference_manager()
        
        # Load user preferences from JSON into memory
        asyncio.create_task(self._load_user_preferences_to_memory())
        
        self.agent = self._create_agent()
    
    def _create_model_client(self):
        """Create and configure the model client (OpenAI or Azure OpenAI)."""
        # Check if Azure OpenAI configuration is available
        azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        # If Azure OpenAI configuration is provided, use Azure OpenAI
        if azure_openai_deployment and azure_openai_endpoint and azure_openai_api_key:
            # Get Azure configuration from environment variables
            azure_openai_model = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
            azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")
            
            self.logger.info(f"Creating Azure OpenAI model client with deployment: {azure_openai_deployment}, model: {azure_openai_model}, temperature: {self.temperature}")
            
            # Initialize Azure OpenAI client
            return AzureOpenAIChatCompletionClient(
                azure_deployment=azure_openai_deployment,
                model=azure_openai_model,
                api_version=azure_openai_api_version,
                azure_endpoint=azure_openai_endpoint,
                api_key=azure_openai_api_key,
                temperature=self.temperature,
            )
        else:
            # Use standard OpenAI
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
                content=default_profile,
                mime_type=MemoryMimeType.JSON,
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
        
        MEMORY USAGE:
        - You have access to conversation history and user preferences through your memory system
        - User preferences are automatically saved to a JSON file for persistence across sessions
        - Use this information to provide personalized responses and remember user preferences
        - When users mention preferences, update them immediately using the preference management functions
        - Always prioritize user-specified preferences over default assumptions
        
        For general real estate advice, market education, process explanations, or casual conversation, respond directly from your knowledge without using property search functions, but always consider user preferences when relevant and update preferences when mentioned.
        
        Be professional, accurate, and helpful. When providing property information from searches,
        include relevant details like area, price, amenities, and location that match user preferences.
        
        Keep your responses conversational and easy to understand. Format property information clearly.
        """

        self.logger.debug("System message created for agent")
        
        # Create the assistant agent with function calling tools and memory
        agent = AssistantAgent(
            name="RealEstateAgent",
            system_message=system_message,
            model_client=self.model_client,
            tools=REAL_ESTATE_TOOLS,
            memory=[self.memory],  # Add memory to the agent
            reflect_on_tool_use=False, # Disable reflection to avoid unnecessary complexity
            max_tool_iterations=10,  # Limit to 10 function calls per interaction
        )
        
        self.logger.info(f"AssistantAgent created with {len(REAL_ESTATE_TOOLS)} tools and memory integration")
        return agent
    
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
        self.logger.info("Starting interactive chat session")
        
        print("🏠 Real Estate Chat Agent with Memory & Streaming")
        print("=" * 60)
        print("Welcome! I'm your real estate assistant with memory capabilities.")
        print("I'll remember your preferences and conversation history to provide personalized assistance!")
        print("� Your preferences are automatically saved to 'user_preferences.json' file.")
        print("🤖 I can automatically update your preferences based on our conversation!")
        print("�💡 Tip: Messages will stream in real-time as they're generated.")
        print("Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("Type 'memory' to see what I remember about our conversation.")
        print("Type 'preferences' to see your current preferences.")
        print("Type 'clear memory' to clear my memory.")
        print("Type 'update preference [key] [value]' to update a specific preference.")
        print("Logs are being saved to 'real_estate_agent.log' file.")
        print(f"📁 Preferences file location: {self.preference_manager.preferences_file}")
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    self.logger.info("User ended the conversation")
                    print("👋 Thank you for chatting! Have a great day!")
                    break
                
                if user_input.lower() == 'memory':
                    await self._show_memory_contents()
                    continue
                
                if user_input.lower() == 'preferences':
                    await self._show_user_preferences()
                    continue
                
                if user_input.lower() == 'clear memory':
                    await self.clear_memory()
                    # Reload preferences from JSON file after clearing memory
                    await self._load_user_preferences_to_memory()
                    print("🧠 Memory cleared successfully! Preferences reloaded from JSON file.")
                    continue
                
                if user_input.lower().startswith('update preference'):
                    await self._handle_preference_update(user_input)
                    continue
                
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
    
    async def _show_memory_contents(self):
        """Display current memory contents to the user."""
        try:
            # Query all memories (empty query typically returns all in ListMemory)
            memories = await self.memory.query("")
            
            if not memories:
                print("🧠 Memory is currently empty.")
                return
            
            print("🧠 Current Memory Contents:")
            print("=" * 30)
            
            # Group memories by category
            categories = {}
            for memory in memories:
                metadata = memory.metadata or {}
                category = metadata.get('category', 'general')
                if category not in categories:
                    categories[category] = []
                categories[category].append(memory)
            
            for category, items in categories.items():
                print(f"\n📁 {category.title()}:")
                for i, memory in enumerate(items, 1):
                    content = memory.content[:100] + "..." if len(memory.content) > 100 else memory.content
                    print(f"  {i}. {content}")
            
            print("=" * 30)
            
        except Exception as e:
            self.logger.error(f"Error showing memory contents: {e}")
            print(f"❌ Error retrieving memory contents: {e}")
    
    async def _show_user_preferences(self):
        """Display current user preferences from JSON file."""
        try:
            # Get preferences directly from JSON file
            json_preferences = self.preference_manager.get_preferences()
            
            if not json_preferences:
                print("👤 No user preferences found in JSON file.")
                return
            
            print("👤 Current User Preferences (from JSON file):")
            print("=" * 50)
            
            # Show user profile
            user_profile = json_preferences.get("user_profile", {})
            if any(v for v in user_profile.values() if v not in [None, "", "Updated at:"]):
                print("\n📋 User Profile:")
                for key, value in user_profile.items():
                    if value and key != "updated_at":
                        print(f"  • {key.replace('_', ' ').title()}: {value}")
                    elif key == "updated_at" and value:
                        print(f"  • Last Updated: {value}")
            
            # Show property preferences
            property_prefs = json_preferences.get("property_preferences", {})
            if any(v for v in property_prefs.values() if v not in [None, [], "", "Updated at:"]):
                print("\n🏠 Property Preferences:")
                for key, value in property_prefs.items():
                    if value and key != "updated_at":
                        if isinstance(value, list) and value:
                            print(f"  • {key.replace('_', ' ').title()}: {', '.join(map(str, value))}")
                        elif not isinstance(value, list):
                            print(f"  • {key.replace('_', ' ').title()}: {value}")
                    elif key == "updated_at" and value:
                        print(f"  • Last Updated: {value}")
            
            # Show search history count
            search_history = json_preferences.get("search_history", [])
            if search_history:
                print(f"\n🔍 Search History: {len(search_history)} searches recorded")
            
            # Show recent interests
            context = json_preferences.get("conversation_context", {})
            recent_interests = context.get("recent_interests", [])
            if recent_interests:
                print(f"\n💭 Recent Interests: {', '.join(recent_interests)}")
            
            print("=" * 50)
            print(f"📁 Preferences saved in: {self.preference_manager.preferences_file}")
            
        except Exception as e:
            self.logger.error(f"Error showing user preferences: {e}")
            print(f"❌ Error retrieving user preferences: {e}")
    
    async def _handle_preference_update(self, user_input: str):
        """Handle preference update commands."""
        try:
            # Parse the update command: "update preference [key] [value]"
            parts = user_input.split(' ', 3)
            if len(parts) < 4:
                print("❌ Invalid format. Use: update preference [key] [value]")
                print("Example: update preference budget 3000000")
                return
            
            _, _, key, value = parts
            await self.update_user_preference(key, value, "updated")
            print(f"✅ Updated preference '{key}' to '{value}'")
            
        except Exception as e:
            self.logger.error(f"Error handling preference update: {e}")
            print(f"❌ Error updating preference: {e}")
    
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
    # setup_logging("INFO", enable_file_logging=True)
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
