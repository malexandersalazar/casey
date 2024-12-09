import json
import uuid
import traceback
import threading
from queue import Queue
from datetime import datetime

from groq import Groq
from dataclasses import dataclass

@dataclass
class VideoCreationRequest:
    id: str
    gen_params: dict
    status: str = "pending"
    created_at: datetime = datetime.now()

class VideoCreationProcessor:
    
    def __init__(self, groq_api_key, groq_interaction_model_id, groq_notification_model_id, telegram_service, open_ai_service, runway_service):
        self.groq_client = Groq(api_key=groq_api_key)
        self.groq_interaction_model_id = groq_interaction_model_id
        self.groq_notification_model_id = groq_notification_model_id
        self.telegram_service = telegram_service
        self.open_ai_service = open_ai_service
        self.runway_service = runway_service
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

    def __detect_image_parameters(self, topic, user_message):               
        prompt = f"""You are a helpful assistant that extracts, infers, or formulates cohesive image and video generation prompts from user messages. You create prompts suitable for AI image generators (like DALL-E, Stable Diffusion, or FLUX.1) and video generation tools (like Runway).

Your task is to:
1. Extract or infer the key visual elements and descriptive details from the user's message
2. Create an image generation prompt that will serve as the base for the video
3. Create a video generation prompt that describes the motion or transformation desired
4. Return the information in a JSON format

Guidelines for image prompt creation:
- Preserve the user's core intent and desired outcome
- Consider how the image will work as a starting point for the video

Guidelines for video prompt creation:
- Keep descriptions clear and focused on motion or transformation
- Ensure the motion prompt naturally extends from the base image
- Use simple, direct language that describes the desired animation
- Focus on one primary motion or transformation
- Avoid complex or multiple simultaneous actions
- Consider technical limitations of AI video generation

Example pairs of image and video prompts:

1. Nature Scene:
   - Image: "A lone cherry blossom tree in full bloom against a sunset sky"
   - Video: "Petals gently falling in the breeze"

2. Character:
   - Image: "A serene koi fish in crystal clear water, traditional Japanese art style"
   - Video: "The koi fish gracefully swimming forward"

3. Landscape:
   - Image: "A sweeping desert landscape with golden sand dunes at twilight"
   - Video: "Sand shifting and flowing across the dunes"

4. Urban:
   - Image: "A neon-lit cyberpunk city street in the rain"
   - Video: "Rain droplets falling as neon lights flicker"

5. Abstract:
   - Image: "A spiral galaxy of vibrant watercolors on black background"
   - Video: "The galaxy slowly spinning and expanding"

Return JSON format:
{{
    "image_gen_prompt": string or null,
    "video_gen_prompt": string or null
}}

Extract image and video generation prompts from this message:

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
        print('[VideoCreationProcessor] __detect_image_parameters.parsed_result:', parsed_result)
        return parsed_result


    def __generate_processing_message(self, gen_params: dict, last_user_message: str) -> str:
        prompt = f"""Generate an engaging and concise response about the video being generated that will be sent to the user's Telegram.

**Mention general thoughts about the video concept based on these specific details:**
Video prompt: {gen_params['video_gen_prompt']}
User's original message: '''{last_user_message}'''

**The response should:**
1. Acknowledge the image creation request
2. Briefly describe the visual concept being generated
3. Mention that they'll receive a notification when it's ready
"""
        
        print('[VideoCreationProcessor] __generate_processing_message.prompt:', prompt)

        response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.groq_notification_model_id,
                max_tokens=192,
                temperature=0.08,
                frequency_penalty=1.1,
                stream=False)
        
        response_text = response.choices[0].message.content
        print('[VideoCreationProcessor] __generate_processing_message.response_text:', response_text)
        return response_text

    def __process_content(self, request: VideoCreationRequest) -> str:
        print('[VideoCreationProcessor] __process_content.request:', request)
        prompt_image = self.open_ai_service.generate_image(request.gen_params['image_gen_prompt'])
        print('[VideoCreationProcessor] __process_content.prompt_image:', prompt_image)
        task_id = self.runway_service.create_video(prompt_image, request.gen_params['video_gen_prompt'])
        print('[VideoCreationProcessor] __process_content.task_id:', task_id)
        video_url = self.runway_service.retrieve_video(task_id)
        print('[VideoCreationProcessor] __process_content.video_url:', video_url)
        return video_url

    def handle_content_request(self, topic, last_user_message: str) -> str:
        gen_params = self.__detect_image_parameters(topic, last_user_message)
        request = VideoCreationRequest(
            id=str(uuid.uuid4()),
            gen_params=gen_params
        )
        self.content_queue.put(request)
        return self.__generate_processing_message(gen_params, last_user_message)