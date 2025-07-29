# Real Estate Chat Agent with Function Calling & Memory

A sophisticated real estate chat agent built with Microsoft AutoGen that uses function calling to query property and project data from a comprehensive database, with **ListMemory** integration for personalized user experiences.

## Features

### 🧠 Memory System (NEW!)

The agent now includes **ListMemory** functionality that provides:

- **User Preference Storage**: Automatically detects and stores user preferences (budget, location, property type, investment goals)
- **Conversation Context**: Maintains conversation history for better context awareness
- **Personalized Responses**: Uses stored memories to provide tailored recommendations
- **Memory Management**: Users can view, query, and clear stored memories
- **Persistent Context**: Remembers preferences across the conversation session

#### Memory Categories:
- **Budget**: Price ranges, affordability preferences
- **Location**: Area preferences, proximity requirements
- **Property Type**: Condo, house, villa, commercial preferences
- **Investment**: ROI expectations, rental yield preferences
- **Conversation Context**: Previous questions and responses

### Function Calling Capabilities

The agent has access to the following function calling tools:

- **Property Search**: Search properties by bedrooms, bathrooms, area, balcony, furnished status
- **Property Details**: Get detailed information and summaries for specific properties
- **Project Search**: Search real estate projects by developer, location, status, market segment
- **Statistics**: Get comprehensive statistics about properties and projects
- **Amenities**: Retrieve internal and surrounding amenities for projects
- **Group Operations**: Get properties belonging to specific project groups

### Available Functions

1. `search_properties_by_criteria()` - Search properties with filters
2. `get_property_by_id()` - Get specific property details
3. `get_property_summary()` - Get human-readable property summary
4. `search_projects_by_criteria()` - Search projects with filters
5. `get_project_statistics()` - Get database statistics
6. `get_project_amenities()` - Get project amenities
7. `get_properties_by_group_id()` - Get properties in a group
8. `get_all_properties()` - Get all properties
9. `get_all_property_groups()` - Get all project groups

## Setup

1. **Install Dependencies**:
   ```bash
   pip install poetry
   poetry install
   ```

2. **Set Environment Variables**:
   Create a `.env` file with:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MODEL_NAME=gpt-4o  # optional, defaults to gpt-4o
   TEMPERATURE=0.7    # optional, defaults to 0.7
   ```

3. **Verify Data**:
   The mock data files should be present in `mock_data/`:
   - `mock_property_schema_data.json`
   - `mock_property_group_schema_data.json`

## Usage

### Memory Demo (NEW!)

Test the new memory functionality:

```bash
cd real_estate_agent
python3 memory_demo.py
```

This demo shows:
1. How the agent stores user preferences automatically
2. How memory influences future responses
3. Memory management commands (view, clear)
4. Interactive testing of memory features

### Interactive Chat with Memory

The enhanced chat interface now includes memory commands:

```bash
cd real_estate_agent
python3 chat_agent.py
```

**New Commands:**
- Type `memory` to view stored memories
- Type `clear memory` to clear all memories
- The agent automatically stores preferences mentioned in conversation

### Test Function Calling Tools

First, test that all function calling tools work correctly:

```bash
python3 test_function_calling.py
```

This will test all the individual function calling tools and show their results.

### Run the Function Calling Demo

Run the demo script to see function calling in action:

```bash
python3 demo_function_calling.py
```

This will:
1. Test various queries that trigger function calls
2. Enter interactive mode for testing

### Programmatic Usage

```python
import asyncio
from real_estate_agent.chat_agent import RealEstateChatAgent

async def main():
    agent = RealEstateChatAgent()
    
    # Add user preferences to memory
    await agent.add_user_preference("Budget up to 5 million baht", "budget")
    await agent.add_user_preference("Prefers condos in Bangkok", "location")
    
    # The agent will use both memory context and function calling
    response = await agent.chat("Find me some properties that match my preferences")
    print(response)
    
    # Check what's stored in memory
    memories = await agent.query_memory("")
    print(f"Stored {len(memories)} memories")
    
    await agent.close()

asyncio.run(main())
```

## Example Interactions

### Memory-Enhanced Responses

**Initial conversation:**
```
User: "I'm looking for a 2-bedroom condo in Bangkok with a budget of 5 million baht"
Agent: [Stores budget, property type, and location preferences, then responds with relevant information]
```

**Follow-up conversation:**
```
User: "What should I look for in a good investment property?"
Agent: [Uses stored preferences to provide personalized advice for condos in Bangkok within the budget]
```

### Function Calling Queries

- "How many properties are in your database?"
- "Find all 2-bedroom properties"
- "Search for properties with balconies"
- "Show me Vinhomes projects"
- "What are the project statistics?"
- "Find properties between 50-100 square meters"
- "Tell me about property_001"
- "What amenities does the first project have?"

## Memory System Details

## Memory System Details

### Automatic Preference Detection

The agent automatically detects and stores preferences from user messages:

- **Budget keywords**: "budget", "price", "cost", "afford", "$", "baht", "million"
- **Location keywords**: "bangkok", "location", "area", "district", "near", "close to"
- **Property type keywords**: "condo", "house", "apartment", "villa", "townhouse", "commercial"
- **Investment keywords**: "invest", "investment", "roi", "return", "yield", "rental"

### Memory Operations

```python
# Add user preference
await agent.add_user_preference("Prefers properties near BTS stations", "location")

# Add conversation context
await agent.add_conversation_context("User asked about investment strategies", "investment_query")

# Query memory
results = await agent.query_memory("budget")

# Clear all memory
await agent.clear_memory()
```

### Memory Structure

Each memory item contains:
- **Content**: The actual text/information stored
- **MIME Type**: Text format (MemoryMimeType.TEXT)
- **Metadata**: Category, type, and other contextual information

## Function Calling Architecture

The function calling system works as follows:

1. **Tools Definition**: Functions are defined in `tools.py` with proper type annotations using `Annotated`
2. **Agent Integration**: The AutoGen agent is configured with the `tools` parameter
3. **Automatic Invocation**: When users ask questions, the LLM automatically determines which functions to call
4. **Data Retrieval**: Functions query the mock data and return structured results
5. **Response Generation**: The agent uses the function results to generate natural language responses

## Mock Data Structure

The agent works with two types of data:

- **Properties** (`mock_property_schema_data.json`): Individual property units with features like bedrooms, bathrooms, area, price
- **Property Groups** (`mock_property_group_schema_data.json`): Real estate projects with developer info, amenities, location data

## Development

### Adding New Functions

To add new function calling capabilities:

1. Define the function in `tools.py` with proper type annotations
2. Add the function to the `REAL_ESTATE_TOOLS` list
3. The agent will automatically have access to the new function

### Testing

Run the test suite to verify all functions work:

```bash
python3 test_function_calling.py
```

## Requirements

- Python 3.8+
- OpenAI API key
- Dependencies listed in `pyproject.toml`

## Architecture

- **Chat Agent** (`chat_agent.py`): Main agent using AutoGen with function calling
- **Tools** (`tools.py`): Data access layer and function calling definitions
- **Mock Data**: JSON files containing property and project data
- **Demos**: Example scripts showing function calling capabilities

The agent uses Microsoft's AutoGen framework for conversation management and automatically invokes the appropriate functions based on user queries, providing a seamless experience for real estate information retrieval.
