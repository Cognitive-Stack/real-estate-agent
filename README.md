# Real Estate Chat Agent

A simple chat agent using AutoGen for real estate assistance.

## Features

- Interactive chat interface for real estate queries
- Memory management for user preferences and conversation context
- Support for both OpenAI and Azure OpenAI
- Real estate specific tools and knowledge

## Installation

1. Clone the repository
2. Install dependencies using uv:
   ```bash
   make setup-env
   ```

## Configuration

### OpenAI Configuration

Set the following environment variables for OpenAI:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export MODEL_NAME="gpt-4o"  # Optional, defaults to gpt-4o
export TEMPERATURE="0.7"    # Optional, defaults to 0.7
```

### Azure OpenAI Configuration

Set the following environment variables for Azure OpenAI:

```bash
export AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
export AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_MODEL="gpt-4o"           # Optional, defaults to gpt-4o
export AZURE_OPENAI_API_VERSION="2024-06-01" # Optional, defaults to 2024-06-01
export TEMPERATURE="0.7"                     # Optional, defaults to 0.7
```

**Note**: The agent will automatically detect which configuration to use based on the environment variables. If Azure OpenAI variables are set, it will use Azure OpenAI. Otherwise, it will fall back to standard OpenAI.

## Usage

### Using the Makefile

```bash
# Setup development environment
make setup-env

# Run the application
make run

# Add a new package
make add PACKAGE=requests

# Add a development package
make add-dev PACKAGE=pytest

# Run tests
make test

# Format code
make format

# Clean up
make clean
```

### Direct Usage

```python
from real_estate_agent.chat_agent import RealEstateChatAgent

# Initialize the agent
agent = RealEstateChatAgent()

# Start interactive chat
await agent.start_interactive_chat()
```

## Development

### Available Make Commands

- `make help` - Show all available commands
- `make setup-env` - Setup development environment
- `make install` - Install production dependencies
- `make install-dev` - Install development dependencies
- `make add PACKAGE=name` - Add a new package
- `make add-dev PACKAGE=name` - Add a development package
- `make remove PACKAGE=name` - Remove a package
- `make update` - Update all dependencies
- `make run` - Run the application
- `make test` - Run tests
- `make lint` - Run linting
- `make format` - Format code
- `make clean` - Clean Python cache files
- `make clean-all` - Clean everything including virtual environment

## Project Structure

```
real-estate-agent/
├── real_estate_agent/
│   ├── __init__.py
│   ├── chat_agent.py      # Main chat agent implementation
│   └── tools_v1.py        # Real estate tools
├── mock_data/             # Mock data for testing
├── pyproject.toml         # Project configuration
├── Makefile              # Build and development commands
└── README.md             # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Submit a pull request
