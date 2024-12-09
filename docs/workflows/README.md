# System Workflows Documentation

## 1. Overview
The system implements several specialized workflows for content generation and processing, each triggered by specific user intents and orchestrated through a central interaction manager. All workflows operate asynchronously using a queue system and provide feedback through Telegram messages.

## 2. Common Components

### Core Technologies
- **Groq LLM**: Used for intent detection and content generation
- **Vector Database (Vectara)**: For semantic search and content storage
- **Python Threading**: For asynchronous processing
- **Queue System**: For managing async requests
- **Telegram API**: For user notifications

### Base Architecture
- All workflows inherit from a common pattern:
  1. Intent detection in `InteractionManager`
  2. Request queueing in respective processors
  3. Asynchronous processing
  4. Result delivery via Telegram

## 3. Workflows

- [Article Writing Workflow](./article_writing_workflow.md): Generates comprehensive articles by analyzing news sources and structuring content
- [Image Generation Workflow](./image_generation_workflow.md): Transforms natural language descriptions into visually striking images using DALL-E's AI image generation capabilities
- [Meme Generation Workflow](./meme_creation_workflow.md): Creates humorous and contextually relevant memes by intelligently matching user requests with appropriate templates and generating optimized text using the Imgflip service
- [Social Media Composing Workflow](./social_media_composing_workflow.md): Crafts platform-specific social media posts by analyzing news context and adapting content to meet the unique requirements and constraints of different social networks
- [Video Creation Workflow](./video_creation_workflow.md): Produces dynamic video content through a two-stage process of generating base images with DALL-E and animating them using Runway's video generation technology.

## 4. Common Features Across Workflows

### Asynchronous Processing
- All workflows use threading for non-blocking operation
- Request queuing ensures orderly processing
- Status updates via Telegram

### Error Handling
- Comprehensive exception catching
- Processing retries where appropriate
- User notification of failures

### Monitoring
- Process tracking through unique request IDs
- Status logging at each stage
- Performance metrics collection

### Scalability
- Queue-based architecture allows for easy scaling
- Service-based design enables component replacement
- Modular structure supports feature addition

This documentation provides a technical overview of each workflow while highlighting the unique aspects and technologies involved in each process. Each workflow is designed to handle specific content generation needs while maintaining a consistent user experience and robust processing architecture.