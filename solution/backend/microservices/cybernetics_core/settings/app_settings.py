import os
from dataclasses import dataclass

@dataclass
class AppSettings:
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_DIR: str
    APP_ENV: str
    GROQ_API_KEY: str
    GROQ_INTERACTION_MODEL_NAME: str
    GROQ_INTERACTION_TEMPERATURE: float
    AZURE_SPEECH_SUBSCRIPTION_KEY: str
    
    @classmethod
    def from_env(cls):
        return cls(
            LOG_LEVEL=os.getenv("LOG_LEVEL"),
            LOG_FORMAT=os.getenv("LOG_FORMAT"),
            LOG_DIR=os.getenv("LOG_DIR"),
            APP_ENV=os.getenv("APP_ENV"),
            GROQ_API_KEY=os.getenv("GROQ_API_KEY"),
            GROQ_INTERACTION_MODEL_NAME=os.getenv("GROQ_INTERACTION_MODEL_NAME"),
            GROQ_INTERACTION_TEMPERATURE=float(os.getenv("GROQ_INTERACTION_TEMPERATURE")),
            AZURE_SPEECH_SUBSCRIPTION_KEY=os.getenv("AZURE_SPEECH_SUBSCRIPTION_KEY")
        )