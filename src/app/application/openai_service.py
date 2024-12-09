import json
from openai import AzureOpenAI

class OpenAIService:

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