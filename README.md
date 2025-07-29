# Real Estate Chat Agent with Function Calling

A sophisticated real estate chat agent built with Microsoft AutoGen that uses function calling to query property and project data from a comprehensive database.

## Features

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

### Interactive Chat

For regular interactive chat:

```bash
python3 -c "import asyncio; from real_estate_agent.chat_agent import RealEstateChatAgent; asyncio.run(RealEstateChatAgent().start_interactive_chat())"
```

### Programmatic Usage

```python
import asyncio
from real_estate_agent.chat_agent import RealEstateChatAgent

async def main():
    agent = RealEstateChatAgent()
    
    # The agent will automatically use function calling
    response = await agent.chat("Find all 2-bedroom properties with balconies")
    print(response)
    
    await agent.close()

asyncio.run(main())
```

## Example Queries That Trigger Function Calling

- "How many properties are in your database?"
- "Find all 2-bedroom properties"
- "Search for properties with balconies"
- "Show me Vinhomes projects"
- "What are the project statistics?"
- "Find properties between 50-100 square meters"
- "Tell me about property_001"
- "What amenities does the first project have?"

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
