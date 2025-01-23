import json
import uuid
from io import BytesIO
from typing import List, Type
from pydantic import BaseModel

from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from domain import Message, MessageRole
from application.contracts.infrastructure import AudioTranscriptor, TextGenerator

class GroqService(AudioTranscriptor, TextGenerator):
    def __init__(self, api_key: str, model_name: str = None, temperature: float=0.08):
        self.groq_client = Groq(api_key=api_key)
        self.chat_groq_client = ChatGroq(api_key=api_key, temperature=temperature, max_tokens=512, model_kwargs={'frequency_penalty': 1.1})
        self.model_name = model_name

    def transcribe_audio(self, file_extension: str, audio_buffer: BytesIO) -> str:
        return self.groq_client.audio.transcriptions.create(
            file=(f"{str(uuid.uuid4())}{file_extension}", audio_buffer),
            model="whisper-large-v3",
            response_format="text",
            language="es"
        )
    
    def generate_text(self, system_prompt: str, messages: List[Message]):
        langchain_messages = [(MessageRole.SYSTEM.value, system_prompt)] + [(msg.role.value, msg.content) for msg in messages]
        chain = self.chat_groq_client | StrOutputParser()
        return chain.invoke(langchain_messages)

    def __generate_model_template(self, model: Type[BaseModel]) -> str:
        json_schema = model.model_json_schema()
        template = {}
        for field_name, field_schema in json_schema.get("properties", {}).items():
            description = field_schema.get("description", f"{field_name} value")
            if field_schema.get("type") == "array":
                template[field_name] = [description]
            else:
                template[field_name] = description
        return json.dumps(template, indent=4)

    def answer_structured(self, system_prompt, messages: List[Message], model: Type[BaseModel]) -> BaseModel:
        model_template = self.__generate_model_template(model)
        langchain_messages = [(MessageRole.SYSTEM.value, system_prompt)] + \
            [(msg.role.value, msg.content) for msg in messages] + \
            [("system", f"Respond to the previous user message in JSON with the following structure:\n\n{model_template}")]
        llm = self.chat_groq_client.with_structured_output(model, method='json_mode')
        return llm.invoke(langchain_messages)