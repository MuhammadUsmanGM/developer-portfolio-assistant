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

from .memory import PersistentMemoryBank
from .tools.content_generator import content_generator
from .tools.github_analyzer import github_analyzer, github_repo_activity
from .tools.memory_query import get_history
from .tools.portfolio_update import portfolio_update
from .tools.portfolio_writer import portfolio_writer

# Initialize persistent memory bank at module level
# This ensures all agents share the same memory instance for consistency
# Design: Singleton pattern for memory ensures data consistency across agents
memory_bank = PersistentMemoryBank()


# ============================================================================
# SPECIALIZED AGENTS (Multi-Agent System)
# ============================================================================

# GitHub Analysis Agent
# Purpose: Specialized agent for GitHub profile and repository analysis
# Behavior: Focuses solely on fetching and structuring GitHub data
# This agent can be used independently or as part of the coordinator workflow
github_analysis_agent = Agent(
    model="gemini-2.5-flash",
    name="github_analyst",
    description="Specialized agent for GitHub profile and repository analysis",
    instruction=(
        "You are a GitHub analysis specialist. Your role is to fetch and analyze "
        "GitHub profiles and repositories. Focus on extracting meaningful insights "
        "from developer activity, commit history, and repository metadata. "
        "Provide structured, accurate data for portfolio generation."
    ),
    tools=[
        github_analyzer,  # Fetches basic profile data
        github_repo_activity,  # Analyzes repository commits and activity
    ]
)


# Content Generation Agent
# Purpose: Specialized agent for generating portfolio content using Gemini
# Behavior: Takes structured GitHub data and generates professional content
# Design: Uses model fallback mechanism to support both free and pro API tiers
content_generation_agent = Agent(
    model="gemini-2.5-flash",
    name="content_generator_agent",
    description="Specialized agent for generating portfolio content using AI",
    instruction=(
        "You are a content generation specialist. Your role is to transform "
        "GitHub data into engaging, professional portfolio content. Generate "
        "content in various formats (LinkedIn posts, blog posts, README files) "
        "with appropriate tone and style. Ensure content is accurate, engaging, "
        "and highlights the developer's achievements effectively."
    ),
    tools=[
        content_generator,  # Uses Gemini to generate content
    ]
)


# Portfolio Writer Agent
# Purpose: Specialized agent for file operations and portfolio management
# Behavior: Handles writing content to files and managing portfolio entries
# Design: Separated from content generation to allow for different output formats
portfolio_writer_agent = Agent(
    model="gemini-2.5-flash",
    name="portfolio_writer_agent",
    description="Specialized agent for writing and managing portfolio files",
    instruction=(
        "You are a portfolio management specialist. Your role is to save generated "
        "content to appropriate files, manage portfolio entries, and ensure "
        "proper formatting. Handle file operations safely with proper error handling."
    ),
    tools=[
        portfolio_writer,  # Writes content to markdown files
    ]
)


# ============================================================================
# COORDINATOR AGENT (Root Agent)
# ============================================================================

# Coordinator Agent (Root Agent)
# Purpose: Orchestrates the multi-agent workflow
# Behavior: Coordinates between specialized agents to complete portfolio updates
# Design: Uses sequential agent pattern - delegates to specialized agents in order
# This agent has access to all tools and can coordinate the full workflow
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
    ]
)
