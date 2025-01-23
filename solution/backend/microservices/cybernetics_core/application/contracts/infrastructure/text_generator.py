from typing import List, Type
from pydantic import BaseModel
from abc import ABC, abstractmethod

from domain import Message

class TextGenerator(ABC):

    @abstractmethod
    def generate_text(self, system_prompt: str, messages: List[Message]) -> str:
        pass

    @abstractmethod
    def answer_structured(self, system_prompt: str, messages: List[Message], model: Type[BaseModel]) -> BaseModel:
        pass
    
