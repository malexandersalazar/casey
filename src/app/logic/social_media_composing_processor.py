import uuid
import traceback
import threading
from queue import Queue
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter

from groq import Groq
from dataclasses import dataclass

@dataclass
class SocialMediaCompositionRequest:
    id: str
    topic: dict
    last_user_message: str
    status: str = "pending"
    created_at: datetime = datetime.now()

class SocialMediaComposingProcessor:
    """
    A processor class for generating AI-powered social media content using various services and APIs.

    This class orchestrates the creation of social media posts by combining news data, vector search,
    and language model capabilities. It processes requests asynchronously using a queue system and
    notifies users via Telegram when content is ready.

    Attributes:
        NEWS_VECTARA_CORPUS_KEY (str): Constant defining the corpus key for news articles.
        client (Groq): Instance of Groq client for AI model interactions.
        groq_interaction_model_id (str): Model ID for main content generation.
        groq_notification_model_id (str): Model ID for notification messages.
        telegram_service: Service for sending Telegram notifications.
        news_service: Service for fetching news articles.
        vectara_service: Service for vector search operations.
        content_queue (Queue): Queue for processing content requests asynchronously.

    Example:
        ```python
        processor = SocialMediaCompositionProcessor(
            groq_api_key="your_key",
            groq_interaction_model_id="model_id",
            groq_notification_model_id="notification_model_id",
            telegram_service=telegram_service,
            news_service=news_service,
            vectara_service=vectara_service
        )

        # Handle a content request
        response = processor.handle_content_request(
            topic={
                "main_topic": "AI Technology",
                "subtopics": ["Machine Learning", "Neural Networks"],
                "target_audience": "Tech professionals",
                "context": "Latest AI developments",
                "tone": "Professional",
                "complexity": "Technical"
            },
            last_user_message="Need a post about recent AI breakthroughs"
        )
        ```
    """
    NEWS_VECTARA_CORPUS_KEY = 'casey_news'

    def __init__(self, groq_api_key, groq_interaction_model_id, groq_notification_model_id, telegram_service, news_service, vectara_service):
        """
        Initialize the SocialMediaCompositionProcessor with required services and API keys.

        Args:
            groq_api_key (str): API key for Groq service.
            groq_interaction_model_id (str): Model ID for main content generation.
            groq_notification_model_id (str): Model ID for notification messages.
            telegram_service: Service instance for Telegram notifications.
            news_service: Service instance for fetching news.
            vectara_service: Service instance for vector search operations.
        """
        self.client = Groq(api_key=groq_api_key)
        self.groq_interaction_model_id = groq_interaction_model_id
        self.groq_notification_model_id = groq_notification_model_id
        self.telegram_service = telegram_service
        self.news_service = news_service
        self.vectara_service = vectara_service
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
   
    def __generate_processing_message(self, topic: dict, last_user_message: str) -> str:
        """Generate an engaging response about content being processed"""
        prompt = f"""Generate an engaging and concise response about social media post being created and will be sended to the user's Telegram.

**Avoid mentioning any general inclusions or outlines, please focus solely on the following specific topic details provided for social media post generation:**:
Main topic: {topic['main_topic']}
Subtopics: {', '.join(topic['subtopics'])}
Target audience: {topic['target_audience']}
Tone: {topic['context']}
Conversation context: {topic['context']}
User's original message: '''{last_user_message}'''

**The response should:**
1. Acknowledge the content request
2. Explain that it will take some time to create quality content
3. Mention that they'll receive a notification when it's ready
4. Be enthusiastic and engaging
"""

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.groq_notification_model_id,
            max_tokens=192,
            temperature=0.08,
            frequency_penalty=1.1,
            stream=False,
        )

        return response.choices[0].message.content
    
    def __transform_sources_to_context(self, sources):
        """
        Transform a list of source dictionaries into an XML-style context string
        
        Args:
            sources (list): List of dictionaries containing source information
            
        Returns:
            str: Formatted context string in XML-style
        """
        # Start the context with the sources opening tag
        context = "<sources>\n"
        
        # Process each source
        for source in sources:
            context += "  <source>\n"
            
            # Add title
            context += f"    <title>{source.get('title', 'Untitled')}</title>\n"
            
            # Add URL
            context += f"    <url>{source.get('url', '')}</url>\n"
            
            # Add content (replacing any problematic characters)
            content = source.get('text', '')
            # Escape any XML special characters if present
            content = (content.replace('&', '&amp;')
                            .replace('<', '&lt;')
                            .replace('>', '&gt;')
                            .replace('"', '&quot;')
                            .replace("'", '&apos;'))
            context += f"    <content>\n      {content}\n    </content>\n"
            
            context += "  </source>\n"
        
        # Close the sources tag
        context += "</sources>"
        
        return context

    # Example usage:
    def __create_prompt_with_context(self, sources, target_audience, tone, complexity, conversation_context, last_user_message):
        """
        Create a complete prompt including the context and instructions
        
        Args:
            sources (list): List of source dictionaries
            desired_length (int): Desired length of the article in words
            
        Returns:
            str: Complete prompt with context and instructions
        """
        # Transform sources into context
        context = self.__transform_sources_to_context(sources)
        
        # Create the full prompt
        prompt = f"""# CONTEXT
{context}

# INSTRUCTIONS:
Create a social media post that:
1. Addresses this hint from prior conversation: '''{conversation_context}'''
2. Is related to the following user message: '''{last_user_message}'''
3. Review points 1 and 2 to infer the target platform (Twitter, LinkedIn/Facebook, Instagram because that influences length and style)
4. Infers emoji usage based on conversation context and message tone
5. Answer only with the final result of the post, do NOT add any additional text related to the task encommeded to you

# PLATFORM SPECIFICATIONS:
Once platform is determined, follow these limits:
- Twitter: Maximum 280 characters
- LinkedIn: Optimal 1200-1500 characters
- Facebook: Optimal 500-1000 characters
- Instagram: Maximum 2200 characters

# STRUCTURE BY PLATFORM:
Apply appropriate structure after platform inference:

Twitter:
- Concise message
- Hashtags (if requested)
- Call to action (if needed)
- Link (if applicable)

LinkedIn/Facebook:
- Hook/Opening line
- Main message (2-3 short paragraphs)
- Call to action
- Relevant hashtags (if requested)

Instagram:
- Engaging opening
- Message body
- Hashtags (if requested)
- Call to action

# STYLE:
- Audience: '{target_audience}'
- Tone: '{tone}'
- Complexity: '{complexity}'

# FORMATTING:
- Use line breaks appropriately for readability
- Place hashtags according to platform best practices
  - Twitter: Integrated into text
  - Instagram: Below main content
  - LinkedIn/Facebook: Minimal, integrated naturally
- Match emoji style and frequency to inferred context

# CONTENT GUIDELINES:
- Start with attention-grabbing opening
- Include clear call-to-action when appropriate
- Use language appropriate to inferred platform
- Incorporate keywords naturally
- Keep message focused on single main point

# TEMPLATE:

[Engaging opening line]

[Main message content]

[Call to action]

[Hashtags if appropriate]

[Link if applicable]
"""

        return prompt
    
    def __split_articles_into_text_chunks(self, articles):
        """
        Splits article text content into smaller, overlapping chunks for processing.
        
        Takes a list of article dictionaries and adds a 'chunks' field containing text segments suitable for embedding or analysis. Chunks smaller than a tweet (280 chars) are filtered out. Articles without valid chunks are removed.

        Args:
            articles (list): List of article dictionaries, each containing a 'text' field with the full article content.

        Returns:
            list: Filtered list of article dictionaries, each containing an additional 'chunks' field with list of chunk dictionaries. Articles with no valid chunks are excluded.

        Example:
            Input article format: [{'text': 'long article content...', ...}]
            Output format: [{'text': 'long article content...', 'chunks': [{'text': 'chunk1...'}, {'text': 'chunk2...'}], ...}]
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=280,
            length_function=len
        )
        for article in articles:
            chunks = text_splitter.split_text(article['text'])
            article['chunks'] = [{'text': chunk} for chunk in chunks if len(chunk) > 280]
        return [article for article in articles if article['chunks']]

    def __process_content(self, request: SocialMediaCompositionRequest) -> str:
        """Process content creation with various APIs and inference"""

        main_topic_subtopics = [request.topic['context']] + [request.topic['main_topic']] + request.topic['subtopics']
        all_bing_articles = self.news_service.search_bing_news(main_topic_subtopics, 5)
        all_bing_articles = self.__split_articles_into_text_chunks(all_bing_articles)

        for bing_article in all_bing_articles:
            self.vectara_service.add_document_to_corpus(self.NEWS_VECTARA_CORPUS_KEY, bing_article['title'], { 'url': bing_article['url'] }, bing_article['chunks'])

        search_results = self.vectara_service.advanced_single_corpus_query(self.NEWS_VECTARA_CORPUS_KEY, f'{request.topic["main_topic"]}: {request.topic["context"]}', 8)

        sources = [
            {
                "title": row["document_metadata"]["title"],
                "url": row["document_metadata"]["url"],
                "text": row["text"]
            }
            for _, row in search_results.iterrows()
        ]
        target_audience = request.topic['target_audience']
        tone = request.topic['tone']
        complexity = request.topic['complexity']
        conversation_context = request.topic['context']
        last_user_message = request.last_user_message

        prompt = self.__create_prompt_with_context(sources, target_audience, tone, complexity, conversation_context, last_user_message)

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.groq_interaction_model_id,
            max_tokens=2048,
            temperature=0.08,
            frequency_penalty=1.1,
            stream=False,
        )
        
        # self.vectara_service.remove_all_documents_and_data_in_a_corpus(self.NEWS_VECTARA_CORPUS_KEY)

        return response.choices[0].message.content
    
    def handle_content_request(self, topic: dict, last_user_message: str) -> str:
        """
        Handle a new content generation request asynchronously.

        Creates a new request and adds it to the processing queue. Returns an immediate
        response message while content generation continues in the background.

        Args:
            topic (dict): Dictionary containing content parameters including:
                - main_topic (str): Primary topic for content
                - subtopics (list): Related subtopics
                - target_audience (str): Intended audience
                - context (str): Content context
                - tone (str): Desired tone
                - complexity (str): Content complexity level
            last_user_message (str): The user's most recent message for context

        Returns:
            str: A processing message indicating that content creation has begun

        Note:
            The actual content will be delivered via Telegram when ready.
        """
        request = SocialMediaCompositionRequest(
            id=str(uuid.uuid4()),
            topic=topic,
            last_user_message=last_user_message
        )
        self.content_queue.put(request)
        return self.__generate_processing_message(topic, last_user_message)