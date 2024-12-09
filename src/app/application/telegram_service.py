import re
import requests


class TelegramService:
    """
    A service class for sending formatted messages to Telegram using the Telegram Bot API.
    
    This class handles message formatting and sending via Telegram's MarkdownV2 format,
    preserving text styling like bold, italic, and headers.
    """

    def __init__(self, api_token: str, chat_id: str):
        """
        Initialize the TelegramService with bot credentials.

        Args:
            api_token (str): The Telegram Bot API token
            chat_id (str): The target chat ID where messages will be sent
        """
        self.api_token = api_token
        self.chat_id = chat_id
    
    def __escape_markdown_v2(self, text: str) -> str:
        """
        Escapes special characters for Telegram's MarkdownV2 format while preserving formatting for bold text.
        
        Args:
            text (str): Input text containing MarkdownV2 formatting.
            
        Returns:
            str: Escaped text formatted for MarkdownV2.
        """
        # Replace **bold** with temporary tokens to preserve them
        text = re.sub(r'\*\*([^\n]+?)\*\*', lambda m: f'⟦BOLD⟧{m.group(1)}⟦/BOLD⟧', text)
        
        # Escape all MarkdownV2 special characters except for the preserved tokens
        escaped_text = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)
        
        # Restore bold formatting by replacing tokens with MarkdownV2 bold markers
        escaped_text = escaped_text.replace('⟦BOLD⟧', '*').replace('⟦/BOLD⟧', '*')
        
        return escaped_text

    def send_message(self, text: str) -> None:
        """
        Send a formatted message to Telegram.

        This method processes the input text to escape special characters while
        preserving markdown formatting, then sends it via Telegram Bot API.

        Args:
            text (str): The message text to send, can include markdown formatting

        Prints:
            The response from Telegram's API after sending the message
        """
        response = requests.get(
            f"https://api.telegram.org/bot{self.api_token}/sendMessage",
            params={
                "chat_id": self.chat_id,
                "text": self.__escape_markdown_v2(text),
                "parse_mode": "MarkdownV2",
            },
        )
        print("Telegram response:\n", response.text)