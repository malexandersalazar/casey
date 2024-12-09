import json
from openai import AzureOpenAI

class OpenAIService:
    """
    A service class for interacting with Azure OpenAI's API for image generation.

    This class provides a simplified interface for generating images using Azure OpenAI's
    DALL-E 3 model through their API. It handles authentication and request formatting,
    returning direct URLs to generated images.

    Attributes:
    api_key (str): API key for authentication with Azure OpenAI.
    endpoint (str): Azure endpoint URL for the OpenAI service.
    azure_openai_client (AzureOpenAI): Client instance for Azure OpenAI API interactions.

    Example:
    ```python
    service = OpenAIService(
        api_key="your_api_key",
        endpoint="https://your-resource.openai.azure.com/"
    )
    
    # Generate an image
    image_url = service.generate_image(
        prompt="A serene mountain landscape at sunset"
    )
    ```
    """
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint
        self.azure_openai_client = AzureOpenAI(
            api_version="2024-02-01",  
            api_key=api_key,  
            azure_endpoint=endpoint
        )

    def generate_image(self, prompt: str) -> str:
        result = self.azure_openai_client.images.generate(
            model="deployment-dall-e-3",
            quality='standard',
            size='1024x1024',
            prompt=prompt,
            n=1
        )

        json_response = json.loads(result.model_dump_json())
        return json_response["data"][0]["url"]