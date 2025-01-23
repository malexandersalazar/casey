from io import BytesIO
from abc import ABC, abstractmethod


class AudioTranscriptor(ABC):
    """Interface for audio transcription services"""

    @abstractmethod
    def transcribe_audio(self, file_extension: str, audio_buffer: BytesIO) -> str:
        """
        Transcribe audio to text

        Args:
            file_extension: Audio file extension
            audio_buffer: Audio content as BytesIO buffer

        Returns:
            Transcribed text
        """
        pass
