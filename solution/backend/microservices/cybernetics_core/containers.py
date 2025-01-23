from typing import cast
from dependency_injector import containers, providers

from settings import AppSettings

from application.contracts.infrastructure import SpeechSynthesizer, AudioTranscriptor, TextGenerator
from application.contracts.persistence import SystemPromptTemplateRepository

from infrastructure.common import LoggingService
from infrastructure.ai import AzureSpeechSynthesizerService, GroqService
from persistence.relational import InMemorySystemPromptRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["apis", "seeders"])

    app_settings = AppSettings.from_env()

    logging_service = providers.Singleton(
        LoggingService,
        log_level=app_settings.LOG_LEVEL,
        log_format=app_settings.LOG_FORMAT,
        log_dir=app_settings.LOG_DIR,
    )

    system_prompt_repository_service: providers.Provider[SystemPromptTemplateRepository] = providers.Singleton(
        InMemorySystemPromptRepository
    )

    audio_transcriptor_service: providers.Provider[AudioTranscriptor] = providers.Singleton(
        GroqService,
        api_key=app_settings.GROQ_API_KEY
    )

    text_generator_service: providers.Provider[TextGenerator] = providers.Singleton(
        GroqService,
        api_key=app_settings.GROQ_API_KEY,
        model_name=app_settings.GROQ_INTERACTION_MODEL_NAME,
        temperature=app_settings.GROQ_INTERACTION_TEMPERATURE
    )

    speech_synthesizer_service: providers.Provider[SpeechSynthesizer] = providers.Singleton(
        AzureSpeechSynthesizerService,
        azure_speech_subscription_key=app_settings.AZURE_SPEECH_SUBSCRIPTION_KEY,
    )
