import uuid
import traceback
import threading
from queue import Queue
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter

from groq import Groq
from dataclasses import dataclass

@dataclass
class ArticleWritingRequest:
    id: str
    topic: dict
    last_user_message: str
    status: str = "pending"
    created_at: datetime = datetime.now()

class ArticleWritingProcessor:
    NEWS_VECTARA_CORPUS_KEY = 'casey_news'

    def __init__(self, groq_api_key, groq_interaction_model_id, groq_notification_model_id, telegram_service, news_service, vectara_service, semantic_memory_module):
        self.client = Groq(api_key=groq_api_key)
        self.groq_interaction_model_id = groq_interaction_model_id
        self.groq_notification_model_id = groq_notification_model_id
        self.telegram_service = telegram_service
        self.news_service = news_service
        self.vectara_service = vectara_service
        self.semantic_memory_module = semantic_memory_module
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
                    self.semantic_memory_module.crystallize_knowledge(content.splitlines()[0], 'article_writing', 'own', content)
                except Exception as e:
                    print(f"Error processing content: {e}")
                    traceback.print_exc()
                self.content_queue.task_done()
                
        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()
   
    def __generate_processing_message(self, topic: dict, last_user_message: str) -> str:
        """Generate an engaging response about content being processed"""
        prompt = f"""Generate an engaging and concise response about content being created and will be sended to the user's Telegram.

**Avoid mentioning any general inclusions or outlines, please focus solely on the following specific topic details provided for content generation:**:
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
    def __create_prompt_with_context(self, sources, target_audience, tone, complexity, conversation_context, last_user_message, desired_length=4096):
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
Create a high-quality article that:
1. Follows the template structure above
2. Addresses this hint from prior conversation: '''{conversation_context}'''
3. Is related to the following user message: '''{last_user_message}'''

# LENGTH AND STRUCTURE:
- Maximum: {desired_length} characters (including spaces)
- Include: Headline, lead paragraph, key points, and conclusion
- Format: Short paragraphs (2-4 sentences)

# STYLE:
- Audience: '{target_audience}'
- Tone: '{tone}'
- Complexity: '{complexity}'
- Include 1-2 relevant quotes when appropriate

# FORMATTING:
- Use UPPERCASE for the TITLE
- Use ** for subheadings
- Use > for quotes
- Keep paragraphs well-spaced
- Put quotes in single-line paragraphs

# CONTENT GUIDELINES:
- Create engaging, topic-specific subheadings that reflect the content
- Avoid generic subheadings like "Introduction" or "Main Points"
- Each subheading should intrigue the reader about the following content
- Subheadings should flow naturally and tell a story

# TEMPLATE:

[ENGAGING TITLE IN UPPERCASE]

[Compelling lead paragraph]

**[Creative subheading reflecting first main point]**
[Content...]

**[Creative subheading reflecting second main point]**
[More content...]

> [Relevant quote]

**[Creative subheading reflecting final point or conclusion]**
[More content...]

**Sources**
1. [Source Title/Name] ([URL])
2. [Source Title/Name] ([URL])
3. [Source Title/Name] ([URL])
[Continue numbering for all corresponding sources...]
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

    def __process_content(self, request: ArticleWritingRequest) -> str:
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
            max_tokens=3072,
            temperature=0.08,
            frequency_penalty=1.1,
            stream=False,
        )
        
        # self.vectara_service.remove_all_documents_and_data_in_a_corpus(self.NEWS_VECTARA_CORPUS_KEY)

        print('Full Article Generation:\n\n', response.choices[0].message.content)
        return response.choices[0].message.content
    
    def handle_content_request(self, topic: dict, last_user_message: str) -> str:
        """Handle a new content request"""
        # Create content request
        request = ArticleWritingRequest(
            id=str(uuid.uuid4()),
            topic=topic,
            last_user_message=last_user_message
        )
        
        # Add to processing queue
        self.content_queue.put(request)
        
        # Generate immediate response
        return self.__generate_processing_message(topic, last_user_message)

# # Usage in your main application
# class ContentManager:
#     def __init__(self, llm_client, telegram_token: str, chat_id: str):
#         self.processor = ContentProcessor(llm_client, telegram_token, chat_id)
    
#     def handle_message(self, intent_result: dict) -> str:
#         intent = intent_result["intent"]
        
#         if intent == "create content":
#             return self.processor.handle_content_request(intent_result["topic"])
#         elif intent == "casual conversation":
#             return self.handle_conversation(intent_result["topic"])
#         # Handle other intents...