import json
from groq import Groq

from .meme_creation_processor import MemeCreationProcessor
from .episodic_event_processor import EpisodicEventProcessor
from .video_creation_processor import VideoCreationProcessor
from .article_writing_processor import ArticleWritingProcessor
from .image_generation_processor import ImageGenerationProcessor
from .social_media_composing_processor import SocialMediaComposingProcessor

class InteractionManager:
    def __init__(self, groq_api_key, groq_interaction_model_id, groq_notification_model_id, telegram_service, news_service, vectara_service, imgflip_service, open_ai_service, runway_service, semantic_memory_module):
        self.client = Groq(api_key=groq_api_key)
        self.groq_interaction_model_id = groq_interaction_model_id
        self.groq_notification_model_id = groq_notification_model_id

        self.article_writing_processor = ArticleWritingProcessor(groq_api_key, groq_interaction_model_id, groq_notification_model_id, telegram_service, news_service, vectara_service, semantic_memory_module)
        self.social_media_composing_processor = SocialMediaComposingProcessor(groq_api_key, groq_interaction_model_id, groq_notification_model_id, telegram_service, news_service, vectara_service)
        self.meme_creation_processor = MemeCreationProcessor(groq_api_key, groq_interaction_model_id, groq_notification_model_id, imgflip_service, telegram_service)
        self.image_generation_processor = ImageGenerationProcessor(groq_api_key, groq_interaction_model_id, groq_notification_model_id, telegram_service, open_ai_service)
        self.video_creation_processor = VideoCreationProcessor(groq_api_key, groq_interaction_model_id, groq_notification_model_id, telegram_service, open_ai_service, runway_service)
        self.episodic_event_processor = EpisodicEventProcessor(groq_api_key, groq_interaction_model_id, vectara_service)
        
    def detect_intent_and_topic(self, input: str) -> dict:
        """
        Detect intent and detailed topic information from user input using a Large Language Model.
        Returns a dictionary containing the detected intent and rich topic details.
        """
        prompt = '''You are Casey, an AI assistant that analyzes user input to detect both intent and detailed topic information. You will identify only one intent - the most recent and clearly understandable one - along with its associated topic.

# INTENTS:

1. "casual_conversation"
   - Triggers: General questions, discussions, small talk, opinions
   - Examples: 
     - "What do you think about memes?"
     - "How does video editing work?"
     - "Let's talk about creativity"
   - Does NOT include: Requests for content creation

2. "article_writing"
   - Triggers: Explicit requests to Casey to generate written material
   - Scope: Articles, drafts, blog posts, essays, reports, news updates
   - Examples:
     - "Give me a news update on the earthquake"
     - "Write an article about AI"
     - "Draft a blog post about climate change"
   - Does NOT include: Short responses, lists, brief explanations, social media posts, or article subject suggestions

3. "compose_social_media"
   - Triggers: Requests to create content specifically for social media platforms
   - Scope: Posts, tweets, captions, hashtags
   - Examples:
     - "Write a tweet about the new product launch"
     - "Create an Instagram caption for this photo"
     - "Draft a LinkedIn post about our company milestone"
   - Does NOT include: Long-form content, articles, or casual conversations about social media

4. "create_video"
   - Triggers: ONLY explicit requests for Casey to directly create/generate a video
   - Must include clear indicators like:
     - "You create a video about..."
     - "Generate a video for me about..."
     - "Make me a video that..."
   - Examples of what IS "create_video":
     - "Create a video explaining quantum physics"
     - "Generate a video about my product"
   - Examples of what is NOT "create_video" (these are "casual_conversation"):
     - "How do I create a video about quantum physics?"
     - "What's the best way to make a product video?"
     - "Can you help me plan my video?"
     - "Give me advice on making videos"
     - "What should I include in my video?"

5. "create_meme"
   - Triggers: Explicit requests to Casey to make, design or generate a meme
   - Examples:
     - "Make a meme about programming"
     - "Design a funny meme for social media"
   - Does NOT include: Discussions about memes or meme culture

6. "generate_image"
   - Triggers: Explicit requests to Casey for image generation/creation  
   - Examples of valid "generate_image" requests:
     - "Generate an image of a cat playing piano"
     - "Create a picture of a futuristic city in cyberpunk style"
     - "Draw a red dragon breathing fire, digital art style"
     - "Make an image of mountains at sunset, photorealistic"
   - Examples of what is NOT "generate_image" (these are "casual_conversation"):
     - "How can I generate AI images?"
     - "What makes a good image prompt?"
     - "Can you explain image generation?"

7. "episodic_memory_event"
   - Triggers: Personal experiences, significant events, or memorable interactions shared by the user
   - Must include at least ONE of:
     - Clear temporal context (when something happened)
     - Specific location (where it occurred)
     - Personal involvement or perspective
   - Must also include experiential elements:
     - Actions taken
     - Emotions felt
     - Sensations experienced
     - Interactions with others
   - Examples of valid "episodic_memory_event":
     - "Last week I gave a presentation and felt really nervous"
     - "I visited Paris last summer and the Eiffel Tower was amazing"
     - "My team just launched our product and everyone was so excited"
   - Examples of what is NOT "episodic_memory_event" (these are "casual_conversation"):
     - "I like presentations" (general preference)
     - "Paris is beautiful" (general fact)
     - "Product launches are stressful" (general statement)

# TOPIC ANALYSIS RULES:

1. Choose the most recent intent if multiple are present
2. Extract the following topic components when present:
- main_topic: The primary subject area
- subtopics: Specific aspects or focus points within the main topic
- target_audience: Intended readers/viewers (if specified)
- tone: Desired level of formality and emotional character in the content
- complexity: Desired level of detail or complexity
- context: Any additional context or requirements
3. If any component is not present, use "not_specified"
4. If intent is unclear, default to "casual_conversation"
5. Maintain context awareness to avoid intent confusion

# EXAMPLE OUTPUTS:

For "Let's write an article about space exploration, I would like to explain to children the relationship of stars' distance and their colors":
{
    "intent": "article_writing",
    "topic": {
        "main_topic": "space exploration",
        "subtopics": ["stellar distance", "star colors", "astronomical observation"],
        "target_audience": "children",
        "tone": "friendly",
        "complexity": "simplified",
        "context": "explaining the relationship between star distance and observed colors"
    }
}

For "Create a video explaining quantum computing for software developers":
{
    "intent": "create_video",
    "topic": {
        "main_topic": "quantum computing",
        "subtopics": ["quantum principles", "quantum algorithms", "programming implications"],
        "target_audience": "software developers",
        "tone": "technical",
        "complexity": "technical",
        "context": "focus on practical implications for programming"
    }
}

For "How's the weather today?":
{
    "intent": "casual_conversation",
    "topic": {
        "main_topic": "weather",
        "subtopics": ["current conditions"],
        "target_audience": "not_specified",
        "tone": "informative",
        "complexity": "simple",
        "context": "general inquiry"
    }
}

Input: """${input}"""
Return a JSON object about a single and latest intent and detailed topic information.'''

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt.replace("${input}", input)}],
            model=self.groq_interaction_model_id,
            max_tokens=300,
            temperature=0,
            frequency_penalty=1.1,
            stream=False,
            response_format={"type": "json_object"},
        )

        result = response.choices[0].message.content
        print(f"Detected: {result}")

        # Parse and validate the response
        parsed_result = json.loads(result)

        # # Check if we need more topic information for content creation
        # if (
        #     parsed_result["intent"]
        #     in ["create_content", "create_video", "create_meme"]
        #     and parsed_result["topic"]["main_topic"] == "not_specified"
        # ):
        #     print(
        #         "I couldn't identify a specific topic. Can you please provide more details about what you'd like to create?"
        #     )

        return parsed_result
    
    def handle_conversation(self, messages):
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.groq_interaction_model_id,
            max_tokens=1024,
            top_p=0.1,
            stream=False,
            frequency_penalty=1.1
        )
        return chat_completion.choices[0].message.content
   
    def handle_message(self, messages, last_user_message, intent_result: dict) -> str:
        intent = intent_result["intent"]
        
        if intent == "article_writing":
            return self.article_writing_processor.handle_content_request(intent_result["topic"], last_user_message)
        elif intent == "compose_social_media":
            return self.social_media_composing_processor.handle_content_request(intent_result["topic"], last_user_message)
        elif intent == "create_meme":
            return self.meme_creation_processor.handle_content_request(last_user_message)
        elif intent == "generate_image":
            return self.image_generation_processor.handle_content_request(intent_result["topic"], last_user_message)
        elif intent == "create_video":
            print('[InteractionManager] Calling video_creation_processor.handle_content_request')
            return self.video_creation_processor.handle_content_request(intent_result["topic"], last_user_message)
        elif intent == "episodic_memory_event":
            print('[InteractionManager] Calling episodic_event_processor.handle_content_request')
            self.episodic_event_processor.handle_content_request(messages)
            return self.handle_conversation(messages)
        elif intent == "casual_conversation":
            return self.handle_conversation(messages)
        # Handle other intents...
