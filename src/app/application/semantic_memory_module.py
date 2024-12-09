import re
from groq import Groq

class SemanticMemoryModule:
    """
    A module for extracting, processing, and storing semantic knowledge from text content.

    This class processes raw text into discrete, self-contained facts and stores them in a vector
    database for later retrieval. It uses AI language models to extract knowledge and maintains
    semantic relationships while ensuring each fact is independently comprehensible.

    Attributes:
        SEMANTIC_VECTARA_CORPUS_KEY (str): Constant defining the corpus key for semantic knowledge storage.
        groq_client (Groq): Instance of Groq client for AI model interactions.
        groq_interaction_model_id (str): Model ID for knowledge extraction.
        vectara_service: Service for vector database operations.

    Example:
        ```python
        memory = SemanticMemoryModule(
            groq_api_key="your_key",
            groq_interaction_model_id="model_id",
            vectara_service=vectara_service
        )

        # Store knowledge from content
        memory.crystallize_knowledge(
            title="AI Research Paper",
            reason="Research findings",
            source="academic_paper",
            content="Detailed paper content..."
        )
        ```
    """
    SEMANTIC_VECTARA_CORPUS_KEY = 'casey_semantic'

    def __init__(self, groq_api_key, groq_interaction_model_id, vectara_service):
        self.groq_client = Groq(api_key=groq_api_key)        
        self.groq_interaction_model_id = groq_interaction_model_id
        self.vectara_service = vectara_service
        
    def __extract_knowledge(self, content):
        prompt = f'''Extract ALL knowledge from the input text as a collection of completely independent and self-contained facts. Each fact should contain everything necessary to understand it without reference to other facts or external context.

**Keep proper nouns ONLY when they are**:
- Authors of verified scientific discoveries or theories.
- Names of established laws, principles or theories
- Documented patents or technological innovations
- Historical events in which the specific date or place is crucial
- Geographical locations when their specific properties are relevant to the event
- Established scientific measurements or standards

**Instructions for the extraction of each fact**:
- Use generic terms instead of non-essential proper names (e.g., “mammals” instead of specific animal names).
- Replace all relative terms (such as “many,” “some,” “often”) with concrete quantities
- Convert general statements into precise and measurable statements
- Include specific conditions and contexts
- Use exact terminology rather than approximations
- Include all necessary context within the same paragraph
- State all relevant conditions and qualifications
- Define specialized terms within the same fact
- Include all crucial details necessary for understanding
- Include only the information essential to the specific fact
- Eliminate decorative language and unnecessary details
- Focus on one clear point per fact
- Exclude tangential information
- Use clear and literal language
- Avoid metaphors and idioms
- Define potentially ambiguous terms
- Explicitly state relationships
- Use the same terminology for all facts
- Maintain a consistent level of detail
- Ensure that complementary facts do not contradict each other
- Adhere to the technical level of the source material
- Provide sufficient detail for practical understanding
- Include all relevant contextual information

**Output format**:
Your final output should present only and only a simple numbered list of facts, e.g.:
1. [First complete and self-contained fact in a single paragraph].
2. [Second complete and self-contained fact in a single paragraph].
3. [And so on...].

**Each fact must
- Be completely understandable on its own.
- Contain all necessary context and definitions
- Be accurate and unambiguous
- Include only relevant information
- Be expressed in clear and literal language.

**The complete list of facts must retain all the knowledge of the original text without loss of information or context**.

# Input text:
"""
{content}
"""
'''

        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.groq_interaction_model_id,
            max_tokens=8000,
            temperature=0.08,
            frequency_penalty=1.1,
            stream=False
        )

        facts_text = chat_completion.choices[0].message.content

        pattern = r"^\s*(\d+)\.\s+(.+?)(?=\n\s*\d+\.|$)"
        matches = re.finditer(pattern, facts_text, re.MULTILINE | re.DOTALL)
        facts = []
        for match in matches:
            fact = match.group(2).strip()
            facts.append(fact)

        return facts

    def crystallize_knowledge(self, title, reason, source, content):
        fact_list = self.__extract_knowledge(content)
        fact_list_as_document_parts = [{'text': fact} for fact in fact_list]
        self.vectara_service.add_document_to_corpus(self.SEMANTIC_VECTARA_CORPUS_KEY, title, { 'reason': reason, 'source': source }, fact_list_as_document_parts)    