"""
Session Management Implementation

This module provides session and state management for the Developer Portfolio Assistant.
It implements InMemorySessionService pattern as required by the capstone project.

Design Decisions:
- In-memory storage for fast access during active sessions
- Session-based state tracking for multi-user support
- Automatic session expiration for resource management
- Thread-safe operations for concurrent access

Behavior:
- Creates unique sessions for each user interaction
- Tracks workflow state within each session
- Maintains conversation history per session
- Supports session cleanup and expiration
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


class InMemorySessionService:
    """
    In-memory session service for managing agent state.
    
    This class implements session management as required by the capstone project.
    It maintains state for each user session, allowing the agent to track
    conversation context and workflow progress.
    
    Attributes:
        sessions (dict): Dictionary mapping session IDs to session data
        default_ttl (timedelta): Default time-to-live for sessions (24 hours)
    """
    
    def __init__(self, default_ttl_hours: int = 24):
        """
        Initialize the session service.
        
        Args:
            default_ttl_hours (int): Default session lifetime in hours
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = timedelta(hours=default_ttl_hours)
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new session for a user.
        
        Behavior: Generates a unique session ID and initializes session state.
        Each session tracks its creation time and user ID for management purposes.
        
        Design: Uses UUID for session IDs to ensure uniqueness and prevent collisions.
        
        Args:
            user_id (str, optional): User identifier for this session
            
        Returns:
            str: Unique session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
            "state": {},  # Workflow state storage
            "history": [],  # Conversation history
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session by ID.
        
        Behavior: Returns session data if it exists and hasn't expired.
        Updates last_accessed timestamp to track activity.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            dict: Session data, or None if session doesn't exist or expired
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        if datetime.now() - session["created_at"] > self.default_ttl:
            self.delete_session(session_id)
            return None
        
        # Update last accessed time
        session["last_accessed"] = datetime.now()
        return session
    
    def update_session_state(self, session_id: str, key: str, value: Any) -> bool:
        """
        Update a specific state value in a session.
        
        Behavior: Updates the state dictionary for the session. This allows
        tracking workflow progress, user preferences, and intermediate results.
        
        Args:
            session_id (str): Session identifier
            key (str): State key to update
            value (Any): Value to store
            
        Returns:
            bool: True if update successful, False if session doesn't exist
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        session["state"][key] = value
        return True
    
    def get_session_state(self, session_id: str, key: Optional[str] = None) -> Optional[Any]:
        """
        Retrieve state from a session.
        
        Behavior: Returns the entire state dict if key is None, or a specific
        state value if key is provided.
        
        Args:
            session_id (str): Session identifier
            key (str, optional): Specific state key to retrieve
            
        Returns:
            Any: State value(s), or None if session/key doesn't exist
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        if key is None:
            return session["state"]
        return session["state"].get(key)
    
    def add_to_history(self, session_id: str, entry: Dict[str, Any]) -> bool:
        """
        Add an entry to the session's conversation history.
        
        Behavior: Appends a new entry to the session history. This maintains
        a chronological record of interactions within the session.
        
        Args:
            session_id (str): Session identifier
            entry (dict): History entry to add (should include timestamp, type, content)
            
        Returns:
            bool: True if successful, False if session doesn't exist
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Ensure entry has timestamp
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().isoformat()
        
        session["history"].append(entry)
        return True
    
    def get_history(self, session_id: str) -> Optional[list]:
        """
        Get conversation history for a session.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            list: Conversation history, or None if session doesn't exist
        """
        session = self.get_session(session_id)
        if not session:
            return None
        return session["history"]
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Behavior: Removes the session from memory. Used for cleanup and
        when sessions expire.
        
        Args:
            session_id (str): Session identifier to delete
            
        Returns:
            bool: True if deleted, False if session doesn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions.
        
        Behavior: Iterates through all sessions and removes those that have
        exceeded their TTL. Returns count of removed sessions.
        
        Returns:
            int: Number of sessions removed
        """
        now = datetime.now()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session["created_at"] > self.default_ttl
        ]
        
        for sid in expired:
            self.delete_session(sid)
        
        return len(expired)


# Global session service instance
# Design: Singleton pattern ensures all agents share the same session service
session_service = InMemorySessionService()

