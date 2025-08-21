# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangGraph ReAct (Reasoning and Action) agent template built for LangGraph Studio. The agent iteratively reasons about user queries, executes actions using available tools, and provides responses through a cyclic workflow.

## Architecture

### Core Components

- **Graph Definition**: `src/react_agent/graph.py` - Defines the main ReAct agent workflow with `call_model` and `tools` nodes
- **State Management**: `src/react_agent/state.py` - Contains `InputState` and `State` dataclasses that track conversation messages and agent status
- **Context Configuration**: `src/react_agent/context.py` - Defines configurable parameters including model selection and system prompts
- **Tools**: `src/react_agent/tools.py` - Contains available tools for the agent (currently includes authentication tool)
- **Prompts**: `src/react_agent/prompts.py` - System prompts that guide agent behavior
- **Utilities**: `src/react_agent/utils.py` - Helper functions for model loading

### Agent Flow

1. User input enters through `InputState`
2. `call_model` node processes the input using configured LLM
3. `route_model_output` determines if tools are needed or if response is complete
4. If tools are needed, execution moves to `tools` node, then back to `call_model`
5. Cycle continues until final response is generated

## Development Commands

### Testing
```bash
make test                    # Run unit tests
make test TEST_FILE=path     # Run specific test file
make test_watch             # Run tests in watch mode
make extended_tests         # Run extended test suite
```

### Code Quality
```bash
make format                 # Format code with ruff
make lint                   # Run linting and type checking
make spell_check           # Check spelling
```

### Package Management
Uses Poetry for dependency management. Key dependencies:
- `langgraph>=0.6.0,<0.7.0` - Core graph framework
- `langchain-openai`, `langchain-anthropic` - LLM providers
- `langchain-tavily` - Search tool integration

## Configuration

### Environment Setup
1. Copy `.env.example` to `.env`
2. Set required API keys:
   - `ANTHROPIC_API_KEY` (default model: claude-3-5-sonnet-20240620)
   - `OPENAI_API_KEY` (optional)
   - `TAVILY_API_KEY` (for search functionality)

### Model Configuration
Default model in `context.py`: `anthropic/claude-3-5-sonnet-20240620`
Can be changed via runtime context using `provider/model-name` format.

### LangGraph Studio Integration
- Graph definition: `langgraph.json` points to `src/react_agent/graph.py:graph`
- Studio provides visual interface for development and debugging
- Supports hot reload for local development

## State Extensions

The `State` class includes custom fields for user authentication:
- `user_email`: User's email address
- `user_cedula`: User's ID number
- `is_authenticated`: Authentication status

## Tool Development

Tools are defined in `tools.py` and must be callable functions. Current tools:
- `auth_user_tool`: Authenticates users with email and cedula

To add new tools:
1. Define async function in `tools.py`
2. Add to `TOOLS` list
3. Tools automatically bind to model in `call_model` function

## Testing Structure

- Unit tests: `tests/unit_tests/`
- Integration tests: `tests/integration_tests/`
- VCR cassettes: `tests/cassettes/` for recording HTTP interactions