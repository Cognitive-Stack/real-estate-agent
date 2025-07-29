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
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from tools_v1 import REAL_ESTATE_TOOLS

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
        setup_advanced_logging(level, enable_file_logging)
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
        
        
        # Initialize the model client and agent
        self.model_client = self._create_model_client()
        self.agent = self._create_agent()
    
    def _create_model_client(self) -> OpenAIChatCompletionClient:
        """Create and configure the OpenAI model client."""
        self.logger.info(f"Creating OpenAI model client with model: {self.model_name}, temperature: {self.temperature}")
        return OpenAIChatCompletionClient(
            model=self.model_name,
            api_key=self.api_key,
            temperature=self.temperature,
        )
    
    def _create_agent(self) -> AssistantAgent:
        """Create and configure the AutoGen conversable agent."""
        
        self.logger.info("Creating AutoGen AssistantAgent with real estate tools")
        
        # System message defining the agent's role and capabilities
        system_message = f"""
        You are a knowledgeable and helpful real estate assistant. Your role is to:
        
        1. Help users with real estate-related questions
        2. Explain real estate processes, terminology, and market trends
        3. Assist with property valuations and market analysis 
        4. Offer guidance on real estate investments
        5. Help with understanding legal aspects of real estate transactions
        6. Search properties using function calls ONLY when users ask about specific properties or want to search the database
        
        IMPORTANT - When to use function calls:
        - ONLY use function calling tools when users explicitly ask to search for specific properties, contractors, developers, locations, or other database information
        - DO NOT use function calls for: greetings, general questions, explanations, advice, market trends, educational content, or casual conversation
        - Examples that DO NOT need function calls: "hello", "what is a mortgage?", "how does real estate work?", "give me investment advice"
        - Examples that DO need function calls: "find properties in Bangkok", "search for contractors", "show me developers", "look for apartments under $500k"
        
        For general real estate advice, market education, process explanations, or casual conversation, respond directly from your knowledge without using any function calls.
        
        Be professional, accurate, and helpful. When providing property information from searches,
        include relevant details like area, price, amenities, and location.
        
        Keep your responses conversational and easy to understand. Format property information clearly.
        """

        self.logger.debug("System message created for agent")
        
        # Create the assistant agent with function calling tools
        agent = AssistantAgent(
            name="RealEstateAgent",
            system_message=system_message,
            model_client=self.model_client,
            tools=REAL_ESTATE_TOOLS,
            reflect_on_tool_use=False, # Disable reflection to avoid unnecessary complexity
            max_tool_iterations=10,  # Limit to 5 function calls per interaction
        )
        
        self.logger.info(f"AssistantAgent created with {len(REAL_ESTATE_TOOLS)} tools")
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
            
            # Use the Console to stream all messages
            result = await Console(self.agent.run_stream(task=message))
            
            # Extract the final response from the result
            final_response = result.messages[-1].content if result.messages else "No response generated."
            
            self.logger.info(f"Agent response completed: {final_response[:100]}...")
            return final_response
                
        except Exception as e:
            self.logger.error(f"Error in chat method: {str(e)}", exc_info=True)
            return f"An error occurred: {str(e)}"
    
    async def start_interactive_chat(self):
        """Start an interactive chat session in the terminal."""
        self.logger.info("Starting interactive chat session")
        
        print("🏠 Real Estate Chat Agent with Streaming")
        print("=" * 50)
        print("Welcome! I'm your real estate assistant. Ask me anything about real estate!")
        print("💡 Tip: Messages will stream in real-time as they're generated.")
        print("Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("Logs are being saved to 'real_estate_agent.log' file.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    self.logger.info("User ended the conversation")
                    print("👋 Thank you for chatting! Have a great day!")
                    break
                
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
        """Close the model client connection."""
        self.logger.info("Closing model client connection")
        await self.model_client.close()


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
