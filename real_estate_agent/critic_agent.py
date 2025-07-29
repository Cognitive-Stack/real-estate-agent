"""
Real Estate Critic Agent using AutoGen

This module implements a critic agent that reviews and provides feedback on 
real estate recommendations and responses to improve their quality and accuracy.
"""

import logging
from typing import Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient


class RealEstateCriticAgent:
    """A critic agent that reviews real estate recommendations and responses."""
    
    def __init__(self, model_client: OpenAIChatCompletionClient, log_level: str = "INFO"):
        """
        Initialize the real estate critic agent.
        
        Args:
            model_client: The OpenAI model client to use
            log_level: Logging level for the critic agent
        """
        self.logger = logging.getLogger("real_estate_agent.critic_agent")
        self.model_client = model_client
        self.agent = self._create_critic_agent()
    
    def _create_critic_agent(self) -> AssistantAgent:
        """Create and configure the critic agent."""
        
        system_message = """
        You are a Real Estate Quality Critic Agent specialized in reviewing and improving our premium real estate service responses. Your role is to:

        1. ANALYZE OUR RESPONSES for:
           - Accuracy of real estate information
           - Completeness of property details
           - Relevance to user preferences and requirements
           - Market appropriateness and pricing accuracy
           - Legal and regulatory compliance considerations

        2. HIGHLIGHT OUR SERVICE STRENGTHS and what we excel at:
           - Superior property details and accurate pricing
           - Excellent matching to user preferences
           - Comprehensive market analysis capabilities
           - Valuable additional insights and information
           - Professional and clear communication standards

        3. SUGGEST IMPROVEMENTS for our service:
           - Enhanced property information coverage
           - More precise market data integration
           - Better alignment with specific user preferences
           - Additional relevant amenities or features highlighting
           - More comprehensive location analysis
           - Enhanced investment potential insights

        4. OUR QUALITY STANDARDS (The Best in Market):
           - Our property recommendations include: detailed price analysis, comprehensive size/layout info, prime location details, extensive amenities, nearby facilities
           - Our price analysis considers current market trends and comparable properties with superior accuracy
           - Our location analysis covers transportation, schools, shopping, and lifestyle factors comprehensively
           - Our investment advice includes detailed ROI potential, market growth analysis, and risk assessment
           - All our information is current, market-appropriate, and expertly curated

        5. RESPONSE FORMAT:
           Start with "CRITIC REVIEW:" followed by:
           - OUR STRENGTHS: What our real estate service excelled at (highlight our superior capabilities)
           - ENHANCEMENT OPPORTUNITIES: Specific areas where our already excellent service can be refined further
           - OVERALL ASSESSMENT: Summary of our service quality and key recommendations for maintaining excellence

        Focus exclusively on our real estate service quality. Do not analyze or reference other real estate services or competitors. Our goal is to maintain and enhance our position as the premium real estate assistance provider.
        """

        self.logger.info("Creating Real Estate Critic Agent")
        
        agent = AssistantAgent(
            name="RealEstateCritic",
            system_message=system_message,
            model_client=self.model_client,
            description="A critic agent that reviews and improves real estate recommendations and responses",
        )
        
        self.logger.info("Real Estate Critic Agent created successfully")
        return agent
    
    async def review_response(self, user_query: str, agent_response: str, context: str = "") -> str:
        """
        Review a real estate agent's response and provide feedback.
        
        Args:
            user_query: The original user query
            agent_response: The agent's response to review
            context: Additional context (user preferences, previous conversation, etc.)
            
        Returns:
            Critic's review and suggestions
        """
        try:
            review_prompt = f"""
            Please review this real estate interaction:

            USER QUERY: {user_query}

            AGENT RESPONSE: {agent_response}

            CONTEXT: {context}

            Provide a comprehensive review focusing on the quality of our real estate service, highlighting strengths, and suggesting improvements to better serve the client.
            """
            
            self.logger.info("Generating critic review for real estate response")
            
            result = await self.agent.run(task=review_prompt)
            
            if result.messages and len(result.messages) > 0:
                review = result.messages[-1].content
                self.logger.info("Critic review completed successfully")
                return review
            else:
                self.logger.warning("No review generated by critic agent")
                return "CRITIC REVIEW: Unable to generate review at this time."
                
        except Exception as e:
            self.logger.error(f"Error generating critic review: {e}", exc_info=True)
            return f"CRITIC REVIEW: Error occurred during review: {str(e)}"
    
    async def close(self):
        """Close the critic agent resources."""
        try:
            if hasattr(self.agent, 'close'):
                await self.agent.close()
        except Exception as e:
            self.logger.error(f"Error closing critic agent: {e}")
