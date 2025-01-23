import json
import uuid
import traceback
import threading
from queue import Queue
from datetime import datetime

from groq import Groq
from dataclasses import dataclass

@dataclass
class EpisodicEventRegistrationRequest:
    id: str
    params: dict
    status: str = "pending"
    created_at: datetime = datetime.now()

class EpisodicEventProcessor:
    """
    A processor class for detecting and storing episodic memory events from conversations.

    This class analyzes conversations to identify specific, memorable events that qualify as
    episodic memories - those containing temporal context, location, or personal involvement.
    Detected events are stored in a vector database for later retrieval and context.

    Attributes:
    EPISODIC_VECTARA_CORPUS_KEY (str): Constant defining the corpus key for episodic memories.
    groq_client (Groq): Instance of Groq client for language processing.
    groq_interaction_model_id (str): Model ID for event detection.
    vectara_service: Service for vector database operations.
    content_queue (Queue): Queue for processing memory events asynchronously.

    Example:
    ```python
    processor = EpisodicEventProcessor(
        groq_api_key="your_key",
        groq_interaction_model_id="model_id",
        vectara_service=vectara_service
    )

    # Process conversation for episodic events
    processor.handle_content_request([
        {"role": "user", "content": "Last summer, I visited Paris for the first time..."},
        {"role": "assistant", "content": "That sounds wonderful! How was it?"},
        {"role": "user", "content": "The Eiffel Tower was amazing at sunset..."}
    ])
    ```
    """
    EPISODIC_VECTARA_CORPUS_KEY = "casey_episodic"
    
    def __init__(self, groq_api_key, groq_interaction_model_id, vectara_service):
        self.groq_client = Groq(api_key=groq_api_key)
        self.groq_interaction_model_id = groq_interaction_model_id
        self.vectara_service = vectara_service
        self.content_queue = Queue()
        self.__start_processing_thread()

    def __start_processing_thread(self):
        """Start background thread for content processing"""
        def process_queue():
            while True:
                request = self.content_queue.get()
                try:
                    self.__process_content(request)
                except Exception as e:
                    print(f"Error processing content: {e}")
                    traceback.print_exc()
                self.content_queue.task_done()
                
        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()

    def __detect_episodic_memory_parameters(self, user_messages):               
        prompt = f"""# Task: Episodic Memory Event Extraction

You are tasked with analyzing text to identify and extract events that would constitute episodic memories - personal, experiential events that include specific contextual details (time, place, or circumstances) and could be stored in a person's episodic memory.

## What Qualifies as an Episodic Memory Event:
1. Must be a specific, discrete event (not general facts or habits)
2. Must include at least one of:
   - Clear temporal context (when it happened)
   - Specific location (where it happened)
   - Personal involvement or perspective
3. Should be memorable enough to be stored in long-term memory
4. Must include experiential elements (actions, sensations, emotions, or interactions)

## What Does NOT Qualify:
- General facts or knowledge
- Regular routines without specific instances
- Abstract concepts or descriptions
- Hypothetical scenarios
- Future plans
- General preferences or opinions

## Output Format:
Return a JSON object with a single property called "fact". If an episodic event is found, include it as a string. If no qualifying episodic event is found, set the value to "NOEPISODICEVENT".

## Examples:

Input: "Coffee is my favorite morning beverage. I drink it every day."
Output: {{
    "fact": "NOEPISODICEVENT"
}}
Explanation: This is a general preference and routine, not a specific episodic event.

Input: "Last summer, I accidentally dropped my ice cream cone at the beach and a seagull swooped down and grabbed it right in front of me!"
Output: {{
    "fact": "Experienced a seagull stealing dropped ice cream cone at the beach last summer"
}}
Explanation: This is a specific event with time (last summer), place (beach), and unique experience.

Input: "When I was 12, my grandfather taught me how to fish at Lake Michigan. I caught my first bass that day, and he was so proud he took a picture of me holding it."
Output: {{
    "fact": "Learned fishing from grandfather at Lake Michigan at age 12 and caught first bass"
}}
Explanation: This is a specific memory with age, location, people involved, and meaningful outcome.

Input: "Scientists believe that climate change will cause significant problems in the future."
Output: {{
    "fact": "NOEPISODICEVENT"
}}
Explanation: This is general knowledge/prediction, not a specific episodic event.

Input: "I love watching movies on weekends with my family."
Output: {{
    "fact": "NOEPISODICEVENT"
}}
Explanation: This is a habitual activity without a specific instance.

Input: "During my college graduation ceremony in 2019, my cap fell off while I was walking across the stage to receive my diploma, and everyone laughed."
Output: {{
    "fact": "Cap fell off while receiving diploma at college graduation ceremony in 2019"
}}
Explanation: This is a specific event with time, place, and memorable incident.

## Your Task:
Analyze the following text and extract any episodic memory event according to the criteria above. Return your response in the specified JSON format. Remember, if no qualifying episodic event is found, return "NOEPISODICEVENT" as the fact value.

Text to analyze:

'''
{user_messages}
'''
"""

        response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.groq_interaction_model_id,
                max_tokens=1024,
                temperature=0.08,
                stream=False,
                response_format={"type": "json_object"}
                )

        result = response.choices[0].message.content
        parsed_result = json.loads(result)
        print('[EpisodicEventProcessor] __detect_episodic_memory_parameters.parsed_result', parsed_result)
        return parsed_result

    def __process_content(self, request: EpisodicEventRegistrationRequest) -> str:
        if request.params['fact'] == 'NOEPISODICEVENT':
            return
        document_parts = [{'text': request.params['fact']}]
        self.vectara_service.add_document_to_corpus(self.EPISODIC_VECTARA_CORPUS_KEY, request.params['fact'], {}, document_parts)

    def handle_content_request(self, messages):
        user_msgs = [msg for msg in messages if msg["role"] == "user"] 
        user_msgs_json = json.dumps(user_msgs, indent=4)

        params = self.__detect_episodic_memory_parameters(user_msgs_json)
        request = EpisodicEventRegistrationRequest(
            id=str(uuid.uuid4()),
            params=params
        )
        self.content_queue.put(request)