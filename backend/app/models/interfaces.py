from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Retriever(ABC):
    """Abstract base class for product retrieval."""
    
    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant product documents based on a user query."""
        pass


class ChatMemory(ABC):
    """Abstract base class for managing conversational memory."""
    
    @abstractmethod
    async def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to the session's chat history."""
        pass
    
    @abstractmethod
    async def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieve recent chat history for a session."""
        pass
