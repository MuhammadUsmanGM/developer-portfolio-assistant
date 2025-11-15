"""
Developer Portfolio Assistant Agent System

This module implements a multi-agent architecture for automating developer portfolio updates.
The system consists of specialized agents that work together to analyze GitHub profiles,
generate content, and maintain portfolio history.

Architecture:
- Coordinator Agent: Orchestrates the workflow and delegates tasks to specialized agents
- GitHub Analysis Agent: Specialized in fetching and analyzing GitHub data
- Content Generation Agent: Specialized in generating portfolio content using Gemini
- Portfolio Writer Agent: Handles file operations and portfolio updates

Design Decision: Multi-agent architecture allows for:
1. Separation of concerns (each agent has a focused responsibility)
2. Parallel processing capabilities (agents can work concurrently)
3. Better error isolation (failures in one agent don't cascade)
4. Easier testing and maintenance
"""

from google.adk.agents import Agent

from .a2a_protocol import MessageType, a2a_protocol
from .memory import memory_bank
from .tools.a2a_tools import (
    get_a2a_message_history,
    process_a2a_messages,
    send_a2a_event,
    send_a2a_request,
)
from .tools.content_generator import content_generator
from .tools.github_analyzer import github_analyzer, github_repo_activity
from .tools.long_running_tools import (
    create_long_running_operation,
    get_operation_status,
    list_operations,
    pause_operation,
    resume_operation,
)
from .tools.memory_query import get_history
from .tools.portfolio_update import portfolio_update
from .tools.portfolio_writer import portfolio_writer

# Import memory_bank singleton from memory module
# This ensures all agents share the same memory instance for consistency
# Design: Singleton pattern for memory ensures data consistency across agents


def _github_agent_message_handler(message):
    """
    Message handler for GitHub Analysis Agent.

    This function handles A2A messages received by the GitHub Analysis Agent.
    It processes requests and sends responses back through the A2A protocol.

    Design: Enables agent-to-agent communication for the GitHub Analysis Agent.
    Other agents can request GitHub data by sending A2A messages.
    """
    from .utils.logging import log_event

    if message.message_type == MessageType.REQUEST:
        # Handle request for GitHub analysis
        username = message.payload.get("username")
        if username:
            log_event(f"GitHub agent received A2A request for username: {username}")
            # Perform analysis
            result = github_analyzer(username)
            # Send response
            a2a_protocol.send_response(
                from_agent="github_analyst",
                to_agent=message.from_agent,
                payload={"result": result},
                correlation_id=message.message_id,
            )


def _content_agent_message_handler(message):
    """
    Message handler for Content Generation Agent.

    This function handles A2A messages received by the Content Generation Agent.
    It processes content generation requests from other agents.
    """
    from .utils.logging import log_event

    if message.message_type == MessageType.REQUEST:
        # Handle request for content generation
        github_summary = message.payload.get("github_summary")
        if github_summary:
            log_event(f"Content agent received A2A request for content generation")
            # Generate content
            result = content_generator(github_summary)
            # Send response
            a2a_protocol.send_response(
                from_agent="content_generator_agent",
                to_agent=message.from_agent,
                payload={"result": result},
                correlation_id=message.message_id,
            )


def _writer_agent_message_handler(message):
    """
    Message handler for Portfolio Writer Agent.

    This function handles A2A messages received by the Portfolio Writer Agent.
    It processes file writing requests from other agents.
    """
    from .utils.logging import log_event

    if message.message_type == MessageType.REQUEST:
        # Handle request for file writing
        content = message.payload.get("content")
        filename = message.payload.get("filename", "portfolio_entry.md")
        if content:
            log_event(f"Writer agent received A2A request to write file: {filename}")
            # Write file
            result = portfolio_writer(content, filename)
            # Send response
            a2a_protocol.send_response(
                from_agent="portfolio_writer_agent",
                to_agent=message.from_agent,
                payload={"result": result},
                correlation_id=message.message_id,
            )


# ============================================================================
# SPECIALIZED AGENTS (Multi-Agent System)
# ============================================================================

# GitHub Analysis Agent
# Purpose: Specialized agent for GitHub profile and repository analysis
# Behavior: Focuses solely on fetching and structuring GitHub data
# This agent can be used independently or as part of the coordinator workflow
# A2A Integration: Registered with A2A protocol for agent-to-agent communication
github_analysis_agent = Agent(
    model="gemini-2.5-flash",
    name="github_analyst",
    description="Specialized agent for GitHub profile and repository analysis",
    instruction=(
        "You are a GitHub analysis specialist. Your role is to fetch and analyze "
        "GitHub profiles and repositories. Focus on extracting meaningful insights "
        "from developer activity, commit history, and repository metadata. "
        "Provide structured, accurate data for portfolio generation. "
        "You can communicate with other agents via the A2A protocol."
    ),
    tools=[
        github_analyzer,  # Fetches basic profile data
        github_repo_activity,  # Analyzes repository commits and activity
    ],
)

# Register GitHub agent with A2A protocol
# Design: Enables agent-to-agent communication for GitHub analysis requests
a2a_protocol.register_agent("github_analyst", _github_agent_message_handler)


# Content Generation Agent
# Purpose: Specialized agent for generating portfolio content using Gemini
# Behavior: Takes structured GitHub data and generates professional content
# Design: Uses model fallback mechanism to support both free and pro API tiers
# A2A Integration: Registered with A2A protocol for agent-to-agent communication
content_generation_agent = Agent(
    model="gemini-2.5-flash",
    name="content_generator_agent",
    description="Specialized agent for generating portfolio content using AI",
    instruction=(
        "You are a content generation specialist. Your role is to transform "
        "GitHub data into engaging, professional portfolio content. Generate "
        "content in various formats (LinkedIn posts, blog posts, README files) "
        "with appropriate tone and style. Ensure content is accurate, engaging, "
        "and highlights the developer's achievements effectively. "
        "You can communicate with other agents via the A2A protocol."
    ),
    tools=[
        content_generator,  # Uses Gemini to generate content
    ],
)

# Register Content agent with A2A protocol
# Design: Enables agent-to-agent communication for content generation requests
a2a_protocol.register_agent("content_generator_agent", _content_agent_message_handler)


# Portfolio Writer Agent
# Purpose: Specialized agent for file operations and portfolio management
# Behavior: Handles writing content to files and managing portfolio entries
# Design: Separated from content generation to allow for different output formats
# A2A Integration: Registered with A2A protocol for agent-to-agent communication
portfolio_writer_agent = Agent(
    model="gemini-2.5-flash",
    name="portfolio_writer_agent",
    description="Specialized agent for writing and managing portfolio files",
    instruction=(
        "You are a portfolio management specialist. Your role is to save generated "
        "content to appropriate files, manage portfolio entries, and ensure "
        "proper formatting. Handle file operations safely with proper error handling. "
        "You can communicate with other agents via the A2A protocol."
    ),
    tools=[
        portfolio_writer,  # Writes content to markdown files
    ],
)

# Register Writer agent with A2A protocol
# Design: Enables agent-to-agent communication for file writing requests
a2a_protocol.register_agent("portfolio_writer_agent", _writer_agent_message_handler)


# ============================================================================
# COORDINATOR AGENT (Root Agent)
# ============================================================================

# Coordinator Agent (Root Agent)
# Purpose: Orchestrates the multi-agent workflow
# Behavior: Coordinates between specialized agents to complete portfolio updates
# Design: Uses sequential agent pattern - delegates to specialized agents in order
# This agent has access to all tools and can coordinate the full workflow
# A2A Integration: Can communicate with specialized agents via A2A protocol
root_agent = Agent(
    model="gemini-2.5-flash",
    name="dpa_root",
    description="Developer Portfolio Assistant Coordinator Agent",
    instruction=(
        "You are the coordinator agent for the Developer Portfolio Assistant. "
        "Your role is to orchestrate the portfolio update workflow by coordinating "
        "with specialized agents:\n"
        "1. Use github_analyzer and github_repo_activity to gather GitHub data\n"
        "2. Use content_generator to create professional content from the data\n"
        "3. Use portfolio_writer to save the generated content\n"
        "4. Use portfolio_update for the complete automated workflow\n"
        "5. Use get_history to query past portfolio updates\n\n"
        "You can delegate tasks to specialized agents or use tools directly. "
        "You can also communicate with specialized agents via the A2A protocol "
        "for distributed task execution. "
        "Ensure error handling and provide clear feedback to users. "
        "Maintain awareness of the workflow state and handle failures gracefully."
    ),
    tools=[
        # Direct tool access for coordinator
        github_analyzer,
        github_repo_activity,
        content_generator,
        portfolio_writer,
        portfolio_update,  # Complete workflow tool
        get_history,  # Memory query tool
        # A2A Protocol tools for agent-to-agent communication
        send_a2a_request,  # Send requests to other agents
        send_a2a_event,  # Send events to other agents
        get_a2a_message_history,  # Query A2A message history
        process_a2a_messages,  # Process queued messages
        # Long-running operation tools
        create_long_running_operation,  # Create pauseable operations
        pause_operation,  # Pause an operation
        resume_operation,  # Resume a paused operation
        get_operation_status,  # Check operation status
        list_operations,  # List all operations
    ],
)


# Register Coordinator agent with A2A protocol
# Design: Enables coordinator to send requests to specialized agents
def _coordinator_message_handler(message):
    """Handle messages received by the coordinator agent."""
    from .utils.logging import log_event

    log_event(
        f"Coordinator agent received A2A message: {message.message_type.value} from {message.from_agent}"
    )


a2a_protocol.register_agent("dpa_root", _coordinator_message_handler)
