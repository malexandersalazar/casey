## Documentation Structure

### Workflows
Detailed documentation for each processing pipeline:
- [Article Writing Workflow](./workflows/article_writing_workflow.md)
- [Image Generation Workflow](./workflows/image_generation_workflow.md)
- [Meme Creation Workflow](./workflows/meme_creation_workflow.md)
- [Social Media Composing Workflow](./workflows/social_media_composing_workflow.md)
- [Video Creation Workflow](./workflows/video_creation_workflow.md)

### Diagrams
System architecture and process flow visualizations:
- [Workflow components interaction diagrams](./diagrams/workflows)
- [Memory system architecture](./diagrams/memories)

### Capabilities
- [Semantic Memory System](./capabilities/memories/semantic_memory_system.md)
- [Episodic Memory System](./capabilities/memories/episodic_memory_system.md)

### Screenshots

- [Casey Outputs](./screenshots)

## Technical Stack

### Core AI Systems

1. **Language Processing**
   - Groq LLM for content generation and intent detection
   - Azure Cognitive Services for text-to-speech (TTS)
   - Whisper for speech recognition and transcription

2. **Memory Systems**
   - Vectara for:
     - Vector database management
     - Semantic search capabilities
     - RAG (Retrieval-Augmented Generation)
     - Advanced embeddings

3. **Multimodal Generation**
   - OpenAI's DALL-E for image generation
   - RunwayML for video content
   - Imgflip API for meme creation

### Infrastructure

1. **Backend Core**
   - Language: Python
   - Processing: Asynchronous architecture
     - Threading system
     - Queue management
   - Data Formats: JSON, XML

2. **External Integrations**
   - Bing News API for current news/events
   - Telegram API for content delivery/distribution