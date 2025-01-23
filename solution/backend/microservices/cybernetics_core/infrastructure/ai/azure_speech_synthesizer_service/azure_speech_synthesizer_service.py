import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

import azure.cognitiveservices.speech as speechsdk

from application.contracts.infrastructure import SpeechSynthesizer

class AzureSpeechSynthesizerService(SpeechSynthesizer):
    """Azure implementation of speech synthesis"""
    
    def __init__(self, azure_speech_subscription_key: str):
        """
        Initialize Azure Speech Synthesizer
        
        Args:
            azure_speech_subscription_key (str): Azure Speech Subscription Key
        """
        self.upload_dir = "temp_audio"
        self._ensure_upload_dir()
        
        # Configure speech service
        self.speech_config = speechsdk.SpeechConfig(azure_speech_subscription_key, "eastus")
        self.speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Ogg16Khz16BitMonoOpus)
        
        # Voice configurations
        self.voice_configs = {
            'en': {
                'language': 'en-US',
                'voice': 'en-US-AvaMultilingualNeural'
            },
            # 'es': {
            #     'language': 'es-ES',
            #     'voice': 'es-MX-MarinaNeural'
            # }
            'es': {
                'language': 'es-ES',
                'voice': 'es-ES-XimenaMultilingualNeural'
            }
        }

    def _ensure_upload_dir(self) -> None:
        """Create upload directory if it doesn't exist"""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)

    def _generate_unique_filename(self, extension: str = ".opus") -> str:
        """Generate a unique filename using UUID"""
        unique_filename = f"{uuid.uuid4()}{extension}"
        return os.path.join(self.upload_dir, unique_filename)

    def synthesize_speech(self, text: str, language: str = 'es') -> Tuple[Optional[str], Optional[str]]:
        """
        Synthesize speech from text
        
        Args:
            text (str): Text to synthesize
            language (str): Language code ('en' or 'es')
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (file_path, error_message)
        """
        try:
            # Validate language
            if language not in self.voice_configs:
                return None, f"Unsupported language: {language}"

            # Configure voice settings
            voice_config = self.voice_configs[language]
            self.speech_config.speech_synthesis_language = voice_config['language']
            self.speech_config.speech_synthesis_voice_name = voice_config['voice']

            # Generate unique filename
            output_file = self._generate_unique_filename()
            
            # Configure audio output
            audio_config = speechsdk.audio.AudioOutputConfig(
                use_default_speaker=False,
                filename=output_file
            )

            # Create synthesizer
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            # Synthesize speech
            result = speech_synthesizer.speak_text_async(text).get()

            # Check result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return output_file, None
            else:
                error_details = result.properties.get(
                    speechsdk.PropertyId.SpeechServiceResponse_JsonErrorDetails
                )
                return None, f"Speech synthesis failed: {error_details}"

        except Exception as e:
            return None, f"Error during speech synthesis: {str(e)}"