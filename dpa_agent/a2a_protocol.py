"""
Agent-to-Agent (A2A) Protocol Implementation

This module implements the A2A protocol for agent-to-agent communication
as required by the capstone project. It enables agents to communicate,
coordinate, and share information with each other.

Design Decisions:
- Message-based communication for loose coupling
- Request-response pattern for synchronous communication
- Event-based pattern for asynchronous notifications
- Message queue for reliable delivery
- Type-safe message definitions

Behavior:
- Agents can send messages to other agents
- Messages are queued and delivered asynchronously
- Supports request-response and event patterns
- Message routing based on agent names
- Message history for debugging
"""

import json
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .utils.logging import log_event


class MessageType(Enum):
    """Types of A2A messages."""

    REQUEST = "request"  # Request-response pattern
    RESPONSE = "response"  # Response to a request
    EVENT = "event"  # Asynchronous event notification
    BROADCAST = "broadcast"  # Broadcast to all agents


class A2AMessage:
    """
    Represents a message in the A2A protocol.

    Attributes:
        message_id (str): Unique message identifier
        from_agent (str): Sender agent name
        to_agent (str): Recipient agent name (or "*" for broadcast)
        message_type (MessageType): Type of message
        payload (dict): Message payload/data
        timestamp (datetime): When message was created
        correlation_id (str, optional): For request-response correlation
    """

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ):
        """
        Create a new A2A message.

        Args:
            from_agent (str): Sender agent name
            to_agent (str): Recipient agent name
            message_type (MessageType): Message type
            payload (dict): Message payload
            correlation_id (str, optional): Correlation ID for request-response
        """
        self.message_id = f"{from_agent}_{to_agent}_{int(time.time() * 1000)}"
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.payload = payload
        self.timestamp = datetime.now()
        self.correlation_id = correlation_id

    def to_dict(self) -> Dict:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "A2AMessage":
        """Create message from dictionary."""
        msg = cls(
            data["from_agent"],
            data["to_agent"],
            MessageType(data["message_type"]),
            data["payload"],
            data.get("correlation_id"),
        )
        msg.message_id = data["message_id"]
        msg.timestamp = datetime.fromisoformat(data["timestamp"])
        return msg


class A2AProtocol:
    """
    Agent-to-Agent communication protocol implementation.

    This class implements the A2A protocol as required by the capstone project.
    It provides message routing, queuing, and delivery between agents.

    Design: Centralized message broker pattern. All agents register with the
    protocol and messages are routed through this central broker.
    """

    def __init__(self):
        """Initialize the A2A protocol."""
        self.agents: Dict[str, Callable] = {}  # Agent name -> message handler
        self.message_queue: List[A2AMessage] = []
        self.message_history: List[A2AMessage] = []
        self.pending_requests: Dict[str, A2AMessage] = {}  # correlation_id -> request

    def register_agent(self, agent_name: str, message_handler: Callable):
        """
        Register an agent with the A2A protocol.

        Args:
            agent_name (str): Name of the agent
            message_handler (Callable): Function to handle incoming messages
        """
        self.agents[agent_name] = message_handler
        log_event(f"Agent {agent_name} registered with A2A protocol")

    def unregister_agent(self, agent_name: str):
        """
        Unregister an agent.

        Args:
            agent_name (str): Name of the agent to unregister
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            log_event(f"Agent {agent_name} unregistered from A2A protocol")

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> A2AMessage:
        """
        Send a message from one agent to another.

        Behavior: Creates a message and queues it for delivery. For request
        messages, stores the request for response correlation.

        Args:
            from_agent (str): Sender agent name
            to_agent (str): Recipient agent name (or "*" for broadcast)
            message_type (MessageType): Type of message
            payload (dict): Message payload
            correlation_id (str, optional): Correlation ID for request-response

        Returns:
            A2AMessage: The created message
        """
        message = A2AMessage(
            from_agent, to_agent, message_type, payload, correlation_id
        )
        self.message_queue.append(message)
        self.message_history.append(message)

        # Store request for response correlation
        if message_type == MessageType.REQUEST:
            self.pending_requests[message.message_id] = message

        log_event(
            f"A2A message sent: {from_agent} -> {to_agent} ({message_type.value})"
        )
        return message

    def send_request(
        self, from_agent: str, to_agent: str, payload: Dict[str, Any]
    ) -> str:
        """
        Send a request message and return correlation ID.

        Args:
            from_agent (str): Sender agent name
            to_agent (str): Recipient agent name
            payload (dict): Request payload

        Returns:
            str: Correlation ID for tracking the response
        """
        message = self.send_message(from_agent, to_agent, MessageType.REQUEST, payload)
        return message.message_id

    def send_response(
        self,
        from_agent: str,
        to_agent: str,
        payload: Dict[str, Any],
        correlation_id: str,
    ):
        """
        Send a response to a request.

        Args:
            from_agent (str): Sender agent name
            to_agent (str): Recipient agent name
            payload (dict): Response payload
            correlation_id (str): Correlation ID from the original request
        """
        self.send_message(
            from_agent, to_agent, MessageType.RESPONSE, payload, correlation_id
        )

    def send_event(self, from_agent: str, to_agent: str, payload: Dict[str, Any]):
        """
        Send an event notification.

        Args:
            from_agent (str): Sender agent name
            to_agent (str): Recipient agent name (or "*" for broadcast)
            payload (dict): Event payload
        """
        self.send_message(from_agent, to_agent, MessageType.EVENT, payload)

    def process_messages(self):
        """
        Process queued messages and deliver them to agents.

        Behavior: Processes all messages in the queue, routing them to
        appropriate agents based on agent name. Broadcast messages are
        delivered to all registered agents.
        """
        while self.message_queue:
            message = self.message_queue.pop(0)

            if message.to_agent == "*":
                # Broadcast to all agents
                for agent_name, handler in self.agents.items():
                    if agent_name != message.from_agent:
                        try:
                            handler(message)
                        except Exception as e:
                            log_event(
                                f"Error delivering broadcast message to {agent_name}: {str(e)}"
                            )
            elif message.to_agent in self.agents:
                # Deliver to specific agent
                handler = self.agents[message.to_agent]
                try:
                    handler(message)
                except Exception as e:
                    log_event(
                        f"Error delivering message to {message.to_agent}: {str(e)}"
                    )
            else:
                log_event(
                    f"Agent {message.to_agent} not found, message queued for retry"
                )
                # Re-queue for retry (with limit to prevent infinite loops)
                if len(self.message_queue) < 100:
                    self.message_queue.append(message)

    def get_message_history(
        self, agent_name: Optional[str] = None, limit: int = 100
    ) -> List[A2AMessage]:
        """
        Get message history, optionally filtered by agent.

        Args:
            agent_name (str, optional): Filter by agent name
            limit (int): Maximum number of messages to return

        Returns:
            list: List of messages
        """
        if agent_name:
            filtered = [
                msg
                for msg in self.message_history
                if msg.from_agent == agent_name or msg.to_agent == agent_name
            ]
            return filtered[-limit:]
        return self.message_history[-limit:]


# Global A2A protocol instance
# Design: Singleton pattern ensures all agents use the same protocol
a2a_protocol = A2AProtocol()
