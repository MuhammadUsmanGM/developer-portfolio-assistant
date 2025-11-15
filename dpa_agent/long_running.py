"""
Long-Running Operations with Pause/Resume Support

This module provides support for long-running operations that can be paused
and resumed. It implements long-running operations as required by the capstone project.

Design Decisions:
- State persistence allows operations to survive process restarts
- Checkpoint-based pause/resume for granular control
- JSON-based state storage for human readability
- Operation status tracking for monitoring

Behavior:
- Operations can be paused at any checkpoint
- State is persisted to disk for recovery
- Operations can be resumed from last checkpoint
- Supports cancellation and cleanup
"""

import json
import os
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from .utils.logging import log_event


class OperationStatus(Enum):
    """Status of a long-running operation."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LongRunningOperation:
    """
    Manages a long-running operation with pause/resume capabilities.

    This class implements long-running operations as required by the capstone project.
    It allows operations to be paused, resumed, and tracked across process restarts.

    Attributes:
        operation_id (str): Unique identifier for this operation
        status (OperationStatus): Current status of the operation
        checkpoints (list): List of checkpoint data
        state (dict): Current operation state
        created_at (datetime): When the operation was created
        updated_at (datetime): When the operation was last updated
    """

    def __init__(
        self,
        operation_id: str,
        operation_type: str,
        initial_state: Optional[Dict] = None,
    ):
        """
        Initialize a long-running operation.

        Args:
            operation_id (str): Unique identifier for this operation
            operation_type (str): Type of operation (e.g., "portfolio_update")
            initial_state (dict, optional): Initial state for the operation
        """
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.status = OperationStatus.PENDING
        self.checkpoints = []
        self.state = initial_state or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.error_message: Optional[str] = None

    def start(self):
        """Mark the operation as running."""
        self.status = OperationStatus.RUNNING
        self.updated_at = datetime.now()
        log_event(f"Long-running operation {self.operation_id} started")

    def pause(self, checkpoint_data: Optional[Dict] = None):
        """
        Pause the operation at a checkpoint.

        Behavior: Saves current state and checkpoint data, then marks operation as paused.
        The operation can be resumed later from this checkpoint.

        Args:
            checkpoint_data (dict, optional): Data to save at this checkpoint
        """
        if self.status != OperationStatus.RUNNING:
            raise ValueError(f"Cannot pause operation in status: {self.status}")

        checkpoint = {
            "checkpoint_id": len(self.checkpoints),
            "timestamp": datetime.now().isoformat(),
            "state": self.state.copy(),
            "data": checkpoint_data or {},
        }
        self.checkpoints.append(checkpoint)
        self.status = OperationStatus.PAUSED
        self.updated_at = datetime.now()
        log_event(
            f"Long-running operation {self.operation_id} paused at checkpoint {len(self.checkpoints)}"
        )

    def resume(self):
        """
        Resume a paused operation.

        Behavior: Restores state from the last checkpoint and marks operation as running.
        The operation continues from where it was paused.

        Returns:
            dict: The state from the last checkpoint
        """
        if self.status != OperationStatus.PAUSED:
            raise ValueError(f"Cannot resume operation in status: {self.status}")

        if not self.checkpoints:
            raise ValueError("No checkpoints available to resume from")

        last_checkpoint = self.checkpoints[-1]
        self.state = last_checkpoint["state"].copy()
        self.status = OperationStatus.RUNNING
        self.updated_at = datetime.now()
        log_event(
            f"Long-running operation {self.operation_id} resumed from checkpoint {len(self.checkpoints)}"
        )
        return self.state

    def complete(self, result: Optional[Dict] = None):
        """
        Mark the operation as completed.

        Args:
            result (dict, optional): Final result of the operation
        """
        self.status = OperationStatus.COMPLETED
        self.updated_at = datetime.now()
        if result:
            self.state["result"] = result
        log_event(f"Long-running operation {self.operation_id} completed")

    def fail(self, error_message: str):
        """
        Mark the operation as failed.

        Args:
            error_message (str): Error message describing the failure
        """
        self.status = OperationStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.now()
        log_event(f"Long-running operation {self.operation_id} failed: {error_message}")

    def cancel(self):
        """Cancel the operation."""
        self.status = OperationStatus.CANCELLED
        self.updated_at = datetime.now()
        log_event(f"Long-running operation {self.operation_id} cancelled")

    def update_state(self, key: str, value: Any):
        """
        Update the operation state.

        Args:
            key (str): State key to update
            value (Any): Value to store
        """
        self.state[key] = value
        self.updated_at = datetime.now()

    def get_state(self, key: Optional[str] = None) -> Any:
        """
        Get operation state.

        Args:
            key (str, optional): Specific state key, or None for entire state

        Returns:
            Any: State value(s)
        """
        if key is None:
            return self.state
        return self.state.get(key)

    def to_dict(self) -> Dict:
        """Convert operation to dictionary for serialization."""
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "status": self.status.value,
            "checkpoints": self.checkpoints,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "LongRunningOperation":
        """Create operation from dictionary."""
        op = cls(data["operation_id"], data["operation_type"], data.get("state", {}))
        op.status = OperationStatus(data["status"])
        op.checkpoints = data.get("checkpoints", [])
        op.created_at = datetime.fromisoformat(data["created_at"])
        op.updated_at = datetime.fromisoformat(data["updated_at"])
        op.error_message = data.get("error_message")
        return op


class LongRunningOperationManager:
    """
    Manages multiple long-running operations.

    This class provides a centralized way to manage, persist, and resume
    long-running operations across the application.
    """

    def __init__(self, storage_file: str = "long_running_operations.json"):
        """
        Initialize the operation manager.

        Args:
            storage_file (str): File path for persisting operations
        """
        self.storage_file = storage_file
        self.operations: Dict[str, LongRunningOperation] = {}
        self._load_operations()

    def _load_operations(self):
        """Load operations from storage file."""
        if os.path.isfile(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for op_data in data.get("operations", []):
                        op = LongRunningOperation.from_dict(op_data)
                        self.operations[op.operation_id] = op
                log_event(
                    f"Loaded {len(self.operations)} long-running operations from storage"
                )
            except Exception as e:
                log_event(f"Error loading long-running operations: {str(e)}")
                self.operations = {}

    def _save_operations(self):
        """Save operations to storage file."""
        try:
            data = {
                "operations": [op.to_dict() for op in self.operations.values()],
                "updated_at": datetime.now().isoformat(),
            }
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log_event(f"Error saving long-running operations: {str(e)}")

    def create_operation(
        self,
        operation_id: str,
        operation_type: str,
        initial_state: Optional[Dict] = None,
    ) -> LongRunningOperation:
        """
        Create a new long-running operation.

        Args:
            operation_id (str): Unique identifier
            operation_type (str): Type of operation
            initial_state (dict, optional): Initial state

        Returns:
            LongRunningOperation: The created operation
        """
        op = LongRunningOperation(operation_id, operation_type, initial_state)
        self.operations[operation_id] = op
        self._save_operations()
        return op

    def get_operation(self, operation_id: str) -> Optional[LongRunningOperation]:
        """
        Get an operation by ID.

        Args:
            operation_id (str): Operation identifier

        Returns:
            LongRunningOperation: The operation, or None if not found
        """
        return self.operations.get(operation_id)

    def pause_operation(
        self, operation_id: str, checkpoint_data: Optional[Dict] = None
    ):
        """
        Pause an operation.

        Args:
            operation_id (str): Operation identifier
            checkpoint_data (dict, optional): Checkpoint data
        """
        op = self.get_operation(operation_id)
        if op:
            op.pause(checkpoint_data)
            self._save_operations()

    def resume_operation(self, operation_id: str) -> Optional[Dict]:
        """
        Resume a paused operation.

        Args:
            operation_id (str): Operation identifier

        Returns:
            dict: The restored state, or None if operation not found
        """
        op = self.get_operation(operation_id)
        if op:
            state = op.resume()
            self._save_operations()
            return state
        return None

    def list_operations(
        self, status: Optional[OperationStatus] = None
    ) -> list[LongRunningOperation]:
        """
        List operations, optionally filtered by status.

        Args:
            status (OperationStatus, optional): Filter by status

        Returns:
            list: List of operations
        """
        if status is None:
            return list(self.operations.values())
        return [op for op in self.operations.values() if op.status == status]


# Global operation manager instance
# Design: Singleton pattern ensures consistent operation management
operation_manager = LongRunningOperationManager()
