import json
import uuid
import traceback
import threading
from queue import Queue
from datetime import datetime

from groq import Groq
from dataclasses import dataclass

@dataclass
class MemeContentRequest:
    id: str
    meme_params: dict
    status: str = "pending"
    created_at: datetime = datetime.now()

class MemeCreationProcessor:
    
    def __init__(self, groq_api_key, groq_interaction_model_id, groq_notification_model_id, imgflip_service, telegram_service):
        self.groq_client = Groq(api_key=groq_api_key)
        self.groq_interaction_model_id = groq_interaction_model_id
        self.groq_notification_model_id = groq_notification_model_id
        self.imgflip_service = imgflip_service
        self.telegram_service = telegram_service
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

    def __detect_meme_parameters(self, user_message):
        available_memes = self.imgflip_service.list_two_box_meme_names()
                
        prompt = f"""You are a helpful assistant that extracts meme creation parameters from user messages.
Available meme templates are: {', '.join(available_memes)}

Your task is to:
1. Identify which meme template the user wants to use
2. Extract the text they want for the top and bottom of the meme
3. Return the information in a JSON format

Rules:
- If the user doesn't specify a meme template but their message implies a common meme format, suggest an appropriate template
- If you can't confidently match to a template, return null for meme_name
- The text should maintain the user's intent but can be adjusted to fit meme format
- If you can't determine top or bottom text, return null for those fields

Return format:
{{
    "meme_name": string or null,
    "top_text": string or null,
    "bottom_text": string or null
}}

Extract meme parameters from this message: '''{user_message}'''
"""

        response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.groq_interaction_model_id,
                max_tokens=100,
                temperature=0,
                stream=False,
                response_format={"type": "json_object"}
                )

        result = response.choices[0].message.content
        parsed_result = json.loads(result)
        print(parsed_result)
        return parsed_result


    def __generate_processing_message(self, meme_params: dict, last_user_message: str) -> str:
        # """Generate an engaging response about content being processed"""
        prompt = f"""Generate an engaging and concise response about meme being created and will be sended to the user's Telegram.

**Mention general right to the point thoughts about the meme details and please focus solely on the following specific details provided for the meme generation:**:
Meme name: {meme_params['meme_name']}
Top Text: {meme_params['top_text']}
Bottom Text: {meme_params['bottom_text']}
Last user message: '''{last_user_message}'''

**The response should:**
1. Acknowledge the meme creation request
2. Shortly explain your thoughts about that meme
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

    def __process_content(self, request: MemeContentRequest) -> str:
        template = self.imgflip_service.find_template_by_name(request.meme_params['meme_name'])
        meme = self.imgflip_service.create_meme(template['id'], request.meme_params['top_text'], request.meme_params['bottom_text'])
        return meme['url']

    def handle_content_request(self, last_user_message: str) -> str:
        meme_params = self.__detect_meme_parameters(last_user_message)
        request = MemeContentRequest(
            id=str(uuid.uuid4()),
            meme_params=meme_params
        )
        self.content_queue.put(request)
        return self.__generate_processing_message(meme_params, last_user_message)