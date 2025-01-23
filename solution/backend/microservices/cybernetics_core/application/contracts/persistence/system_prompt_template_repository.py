from abc import ABC, abstractmethod
from typing import Optional, List

from domain import SystemPromptTemplate

class SystemPromptTemplateRepository(ABC):
    @abstractmethod
    def register(self, prompt: SystemPromptTemplate) -> None:
        pass
    
    @abstractmethod
    def get_latest(self, agent_type: str) -> Optional[SystemPromptTemplate]:
        pass
    
    @abstractmethod
    def get_version(self, agent_type: str, version: int) -> Optional[SystemPromptTemplate]:
        pass

    @abstractmethod
    def get_all(self) -> List[SystemPromptTemplate]:
        pass