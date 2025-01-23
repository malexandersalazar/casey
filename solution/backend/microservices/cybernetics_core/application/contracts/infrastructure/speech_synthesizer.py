from typing import Optional, Tuple
from abc import ABC, abstractmethod


class SpeechSynthesizer(ABC):
    """Interface for speech synthesis services"""

    @abstractmethod
    def synthesize_speech(
        self, text: str, language: str = "es"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Synthesize text to speech

        Args:
            text: Text to synthesize
            language: Target language code (default: 'es')

        Returns:
            Tuple containing optional path to audio or error message
        """
        pass
