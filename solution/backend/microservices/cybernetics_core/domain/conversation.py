from uuid import UUID, uuid4
from typing import List, Dict, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field

from . import Message
from . import MessageRole

@dataclass
class Conversation:
    """Represents an ongoing conversation with history and associated tasks"""
    id: UUID
    user_id: UUID
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_message(self, role: MessageRole, content: str, metadata: Dict[str, Any] = None) -> Message:
        message = Message(
            id=uuid4(),
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.last_activity = datetime.now(timezone.utc)
        return message
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get recent messages for context window"""
        return self.messages[-limit:]