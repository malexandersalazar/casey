from uuid import UUID
from datetime import datetime, timezone
from dataclasses import dataclass, field

from . import AgentType


@dataclass
class SystemPromptTemplate:
    id: UUID
    agent_type: AgentType
    version: int
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
