from ..memory import PersistentMemoryBank
memory_bank = PersistentMemoryBank()
from typing import Optional

def get_history(username: Optional[str] = None) -> dict:
    """
    Get persistent memory history for a username or all users.
    """
    history = memory_bank.get_history(username)
    return {"history": history}
