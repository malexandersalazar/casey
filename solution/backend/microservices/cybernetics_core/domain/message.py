from uuid import UUID
from typing import Dict, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field

from . import MessageRole

@dataclass
class Message:
    """Represents a single message in a conversation"""
    id: UUID
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)