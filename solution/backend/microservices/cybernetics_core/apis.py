import os
import pytz
import pycountry
from uuid import uuid4
from io import BytesIO
from difflib import SequenceMatcher
from datetime import datetime, timezone

from flask import request, send_file
from dependency_injector.wiring import inject, Provide

from containers import Container

from domain import AgentType, Conversation, MessageRole

from application.models import CasualChatResponse
from application.contracts.persistence import SystemPromptTemplateRepository
from application.contracts.infrastructure import SpeechSynthesizer, AudioTranscriptor, TextGenerator

from infrastructure.common import LoggingService

conversation = Conversation(uuid4(), uuid4())

VALID_EMOTIONS = ["neutral", "joy", "sadness", "anger", "surprise", "fear", "disgust"]

def __normalize_emotion(detected_emotion: str) -> str:
    global VALID_EMOTIONS
    detected_emotion = detected_emotion.lower().strip()
    if detected_emotion in VALID_EMOTIONS:
        return detected_emotion
    similarities = [(emotion, SequenceMatcher(None, detected_emotion, emotion).ratio()) for emotion in VALID_EMOTIONS]
    best_match = max(similarities, key=lambda x: x[1])
    return best_match[0] if best_match[1] > 0.85 else "neutral"

@inject
def upload_audio(
    audio_transcriptor_service: AudioTranscriptor = Provide[Container.audio_transcriptor_service],
    text_generator_service: TextGenerator = Provide[Container.text_generator_service],
    speech_synthesizer_service: SpeechSynthesizer = Provide[Container.speech_synthesizer_service],
    system_prompt_repository_service: SystemPromptTemplateRepository = Provide[Container.system_prompt_repository_service],
    logging_service: LoggingService = Provide[Container.logging_service]
    ):
    global conversation

    file = request.files['audio']
    _, file_extension = os.path.splitext(file.filename)
    transcription = audio_transcriptor_service.transcribe_audio(file_extension, BytesIO(file.read()))

    # Getting current date and time
    user_timezone = request.headers.get('X-Timezone')
    local_time = datetime.now(timezone.utc).astimezone(pytz.timezone(user_timezone))
    formatted_datetime = local_time.strftime("%Y-%m-%d %-I:%M:%S %p")

    # Getting language
    user_locale_str = request.headers.get('X-Locale')
    logging_service.info(f'User locale: {user_locale_str}')
    assistant_language = pycountry.languages.get(alpha_2=user_locale_str[:2]).name
    logging_service.info(f'Assistant language: {assistant_language}')
    
    # Creating system prompt
    system_prompt_template = system_prompt_repository_service.get_latest(AgentType.CASUAL_CHAT)
    system_prompt = system_prompt_template.content.format(currentDateTime = formatted_datetime, currentTimeZone = user_timezone, assistantLanguage = assistant_language)
    logging_service.info(f'System prompt: {system_prompt}')

    conversation.add_message(MessageRole.USER, transcription)
    casual_chat_response: CasualChatResponse = text_generator_service.answer_structured(system_prompt, conversation.get_recent_messages(), CasualChatResponse)
    conversation.add_message(MessageRole.ASSISTANT, casual_chat_response.content)
    logging_service.info(f'Agent response: {casual_chat_response}')
    logging_service.info(f'Conversation messages counts: {len(conversation.messages)}')

    output_file, error_message = speech_synthesizer_service.synthesize_speech(casual_chat_response.content)

    response = send_file(
        output_file,
        mimetype='audio/ogg',
        as_attachment=True,
        download_name=os.path.basename(output_file),
    )

    response.headers['X-Emotion'] = __normalize_emotion(casual_chat_response.emotion)

    return response, 200