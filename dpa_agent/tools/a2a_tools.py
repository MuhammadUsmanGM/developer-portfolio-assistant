"""
A2A Protocol Tools

This module provides tools for using the A2A protocol to enable agent-to-agent
communication. These tools demonstrate A2A protocol usage as required by the capstone project.

Design Decisions:
- Tools wrap A2A protocol functionality for easy use by agents
- Supports request-response and event patterns
- Enables distributed task execution across agents
"""

from typing import Dict, Optional

from ..a2a_protocol import MessageType, a2a_protocol
from ..utils.logging import log_event


def send_a2a_request(to_agent: str, payload: Dict, from_agent: str = "dpa_root") -> str:
    """
    Send an A2A request to another agent.

    This tool enables agent-to-agent communication using the A2A protocol.
    It sends a request message and returns a correlation ID for tracking the response.

    Design: Request-response pattern allows agents to request services from
    other agents, enabling distributed task execution.

    Args:
        to_agent (str): Name of the target agent
        payload (dict): Request payload/data
        from_agent (str): Name of the sending agent (default: "dpa_root")

    Returns:
        str: Correlation ID for tracking the response
    """
    correlation_id = a2a_protocol.send_request(from_agent, to_agent, payload)
    log_event(f"A2A request sent from {from_agent} to {to_agent}: {correlation_id}")
    return correlation_id


def send_a2a_event(to_agent: str, payload: Dict, from_agent: str = "dpa_root"):
    """
    Send an A2A event notification to another agent.

    This tool enables asynchronous event notifications between agents.
    Events are fire-and-forget messages for notifications.

    Design: Event pattern allows agents to notify others of state changes
    or important events without requiring a response.

    Args:
        to_agent (str): Name of the target agent (or "*" for broadcast)
        payload (dict): Event payload/data
        from_agent (str): Name of the sending agent (default: "dpa_root")
    """
    a2a_protocol.send_event(from_agent, to_agent, payload)
    log_event(f"A2A event sent from {from_agent} to {to_agent}")


def get_a2a_message_history(agent_name: Optional[str] = None, limit: int = 50) -> Dict:
    """
    Get A2A message history for an agent.

    This tool retrieves the message history for debugging and monitoring
    agent-to-agent communication.

    Args:
        agent_name (str, optional): Filter by agent name
        limit (int): Maximum number of messages to return

    Returns:
        dict: Message history with list of messages
    """
    messages = a2a_protocol.get_message_history(agent_name, limit)
    return {
        "messages": [msg.to_dict() for msg in messages],
        "count": len(messages),
    }


def process_a2a_messages():
    """
    Process queued A2A messages.

    This tool processes all queued messages in the A2A protocol,
    delivering them to their target agents.

    Design: Message processing is typically done automatically, but this
    tool allows manual processing when needed.
    """
    a2a_protocol.process_messages()
    log_event("A2A messages processed")
