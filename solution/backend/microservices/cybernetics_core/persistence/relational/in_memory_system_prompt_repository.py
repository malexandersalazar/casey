from itertools import chain
from typing import Dict, Optional
from dataclasses import dataclass, field

from domain import SystemPromptTemplate
from application.contracts.persistence import SystemPromptTemplateRepository


@dataclass
class InMemorySystemPromptRepository(SystemPromptTemplateRepository):
    _prompts: Dict[str, Dict[int, SystemPromptTemplate]] = field(default_factory=dict)

    def register(self, prompt: SystemPromptTemplate) -> None:
        if prompt.agent_type not in self._prompts:
            self._prompts[prompt.agent_type] = {}
        self._prompts[prompt.agent_type][prompt.version] = prompt

    def get_latest(self, agent_type: str) -> Optional[SystemPromptTemplate]:
        if agent_type not in self._prompts or not self._prompts[agent_type]:
            return None
        latest_version = max(self._prompts[agent_type].keys())
        return self._prompts[agent_type][latest_version]

    def get_version(self, agent_type: str, version: int) -> Optional[SystemPromptTemplate]:
        return self._prompts.get(agent_type, {}).get(version)
    
    def get_all(self):
        return list(chain.from_iterable(
            version_dict.values() 
            for version_dict in self._prompts.values()
        ))
