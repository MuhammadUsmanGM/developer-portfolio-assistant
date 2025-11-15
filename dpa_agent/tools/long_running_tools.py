"""
Long-Running Operation Tools

This module provides tools for managing long-running operations with pause/resume
capabilities. These tools demonstrate long-running operations as required by the capstone project.

Design Decisions:
- Tools wrap long-running operation functionality for easy use by agents
- Supports operation creation, pause, resume, and status checking
- Enables operations to survive process restarts through persistence
"""

from typing import Dict, Optional

from ..long_running import OperationStatus, operation_manager
from ..utils.logging import log_event


def create_long_running_operation(
    operation_id: str, operation_type: str, initial_state: Optional[Dict] = None
) -> Dict:
    """
    Create a new long-running operation.

    This tool creates a long-running operation that can be paused and resumed.
    Operations are persisted to disk, allowing them to survive process restarts.

    Design: Long-running operations enable workflows that may take significant time
    or need to be interrupted and resumed later.

    Args:
        operation_id (str): Unique identifier for the operation
        operation_type (str): Type of operation (e.g., "portfolio_update")
        initial_state (dict, optional): Initial state for the operation

    Returns:
        dict: Operation details including operation_id and status
    """
    op = operation_manager.create_operation(operation_id, operation_type, initial_state)
    log_event(f"Created long-running operation: {operation_id} ({operation_type})")
    return {
        "operation_id": op.operation_id,
        "operation_type": op.operation_type,
        "status": op.status.value,
    }


def pause_operation(operation_id: str, checkpoint_data: Optional[Dict] = None) -> Dict:
    """
    Pause a long-running operation at a checkpoint.

    This tool pauses an operation, saving its current state. The operation
    can be resumed later from this checkpoint.

    Args:
        operation_id (str): Operation identifier
        checkpoint_data (dict, optional): Data to save at this checkpoint

    Returns:
        dict: Operation status after pausing
    """
    op = operation_manager.get_operation(operation_id)
    if not op:
        return {"error": f"Operation {operation_id} not found"}

    try:
        op.pause(checkpoint_data)
        return {
            "operation_id": op.operation_id,
            "status": op.status.value,
            "checkpoints": len(op.checkpoints),
        }
    except Exception as e:
        return {"error": str(e)}


def resume_operation(operation_id: str) -> Dict:
    """
    Resume a paused long-running operation.

    This tool resumes an operation from its last checkpoint, restoring
    the saved state and continuing execution.

    Args:
        operation_id (str): Operation identifier

    Returns:
        dict: Restored state and operation status
    """
    op = operation_manager.get_operation(operation_id)
    if not op:
        return {"error": f"Operation {operation_id} not found"}

    try:
        state = op.resume()
        return {
            "operation_id": op.operation_id,
            "status": op.status.value,
            "restored_state": state,
        }
    except Exception as e:
        return {"error": str(e)}


def get_operation_status(operation_id: str) -> Dict:
    """
    Get the status of a long-running operation.

    Args:
        operation_id (str): Operation identifier

    Returns:
        dict: Operation status and details
    """
    op = operation_manager.get_operation(operation_id)
    if not op:
        return {"error": f"Operation {operation_id} not found"}

    return {
        "operation_id": op.operation_id,
        "operation_type": op.operation_type,
        "status": op.status.value,
        "checkpoints": len(op.checkpoints),
        "created_at": op.created_at.isoformat(),
        "updated_at": op.updated_at.isoformat(),
        "error_message": op.error_message,
    }


def list_operations(status: Optional[str] = None) -> Dict:
    """
    List all long-running operations, optionally filtered by status.

    Args:
        status (str, optional): Filter by status (pending, running, paused, completed, failed, cancelled)

    Returns:
        dict: List of operations
    """
    if status:
        try:
            filter_status = OperationStatus(status)
            operations = operation_manager.list_operations(filter_status)
        except ValueError:
            return {"error": f"Invalid status: {status}"}
    else:
        operations = operation_manager.list_operations()

    return {
        "operations": [
            {
                "operation_id": op.operation_id,
                "operation_type": op.operation_type,
                "status": op.status.value,
                "checkpoints": len(op.checkpoints),
            }
            for op in operations
        ],
        "count": len(operations),
    }
