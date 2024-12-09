import json
import uuid
import traceback
import threading
from queue import Queue
from datetime import datetime

from groq import Groq
from dataclasses import dataclass

@dataclass
class ImageGenerationRequest:
    id: str
    gen_params: dict
    status: str = "pending"
    created_at: datetime = datetime.now()

class ImageGenerationProcessor:
    
    def __init__(self, groq_api_key, groq_interaction_model_id, groq_notification_model_id, telegram_service, open_ai_service):
        self.groq_client = Groq(api_key=groq_api_key)
        self.groq_interaction_model_id = groq_interaction_model_id
        self.groq_notification_model_id = groq_notification_model_id
        self.telegram_service = telegram_service
        self.open_ai_service = open_ai_service
        self.content_queue = Queue()
        self.__start_processing_thread()

    def __start_processing_thread(self):
        """Start background thread for content processing"""
        def process_queue():
            while True:
                request = self.content_queue.get()
                try:
                    content = self.__process_content(request)
                    self.telegram_service.send_message(content)
                except Exception as e:
                    print(f"Error processing content: {e}")
                    traceback.print_exc()
                self.content_queue.task_done()
                
        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()

    def __detect_image_parameters(self, topic:dict, user_message:str):               
        prompt = f"""You are a helpful assistant that extracts, infers, or formulates image generation prompts from user messages for AI image generators like DALL-E, Stable Diffusion, or FLUX.1.

Your task is to:
1. Extract or infer the key visual elements and descriptive details from the user's message
2. Format these details into a clear, detailed prompt suitable for AI image generation
3. Return the information in a JSON format

Guidelines for prompt creation:
- Specify important details about lighting, perspective, and composition when relevant
- Maintain artistic coherence in the description
- Preserve the user's core intent and desired outcome

Return format:
{{
    "image_gen_prompt": string or null
}}

Extract image generation prompt from this message:

'''
**{topic['main_topic']}: {topic['context']}**

{user_message}
'''
"""

        response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.groq_interaction_model_id,
                max_tokens=192,
                temperature=0.08,
                stream=False,
                response_format={"type": "json_object"}
                )

        result = response.choices[0].message.content
        parsed_result = json.loads(result)
        print(parsed_result)
        return parsed_result


    def __generate_processing_message(self, gen_params: dict, last_user_message: str) -> str:
        prompt = f"""Generate an engaging and concise response about the image being generated that will be sent to the user's Telegram.

**Mention general thoughts about the image concept based on these specific details:**
Image prompt: {gen_params['image_gen_prompt']}
User's original message: '''{last_user_message}'

**The response should:**
1. Acknowledge the image creation request
2. Briefly describe the visual concept being generated
3. Mention that they'll receive a notification when it's ready
"""

        response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.groq_notification_model_id,
                max_tokens=192,
                temperature=0.08,
                frequency_penalty=1.1,
                stream=False)

        response_text = response.choices[0].message.content
        return response_text

    def __process_content(self, request: ImageGenerationRequest) -> str:
        return self.open_ai_service.generate_image(request.gen_params['image_gen_prompt'])

    def handle_content_request(self, topic, last_user_message: str) -> str:
        gen_params = self.__detect_image_parameters(topic, last_user_message)
        request = ImageGenerationRequest(
            id=str(uuid.uuid4()),
            gen_params=gen_params
        )
        self.content_queue.put(request)
        return self.__generate_processing_message(gen_params, last_user_message)