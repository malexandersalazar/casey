# Casey: Voice-Activated AI Companion for Mental Wellbeing & Content Creation

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

Casey is a voice-activated AI companion powered by an advanced dual memory system that enables both personalized interactions and specialized knowledge applications. While currently focused on mental wellbeing support, Casey's semantic memory system is designed to process and utilize knowledge from any specialized field - from psychology to literature, science, or history. We've chosen to prioritize mental health support by loading it with professional psychological resources, making it particularly valuable for vulnerable populations with limited access to mental health resources.

Through its unique episodic memory system, Casey remembers your significant life events, personal milestones, and meaningful experiences, enabling conversations informed by your personal context. This long-term memory allows Casey to provide consistent support while understanding your individual journey over time. Meanwhile, its semantic memory system continuously processes information from established resources, currently building upon a foundation of mental health knowledge from official guides, books, and publications.

These advanced memory capabilities work alongside powerful language models, computer vision, and speech processing technologies to create a companion that adapts to your needs. Casey helps you create and manage multi-format content hands-free, making it valuable for professionals who need hands-free content creation and those requiring accessibility accommodations. Through natural voice interaction, Casey eliminates the need for typing or technical expertise, offering both evidence-based support and practical assistance.
The combination of episodic and semantic memory systems makes Casey highly adaptable, with the potential to serve as a specialized companion across various knowledge domains. Our current focus on mental wellbeing reflects an urgent social need rather than a technical limitation of the system.

Here's an updated and more comprehensive list of key features that better reflects Casey's full capabilities:

## Key Features

- 🎙️ **Voice-First Interaction**:
   - Completely hands-free operation, eliminating need for technical expertise or typing
- 🧠 **Advanced Memory Systems**:
  - Episodic memory for personal context and experience tracking
  - Semantic memory adaptable to any knowledge domain (currently focused on mental wellbeing)
- 🤝 **Mental Wellbeing Support**:
  - Evidence-based psychological guidance
  - Consistent emotional support
  - Crisis awareness and appropriate responses
- 📰 **Multi-Format Content Creation**:
  - Automatic retrieval and analysis of relevant news
  - Articles and written content 
  - Social media posts
  - Images through DALL-E
  - Videos through RunwayML
  - Memes and visual content
- ♿ **Universal Accessibility**:
  - Voice-first design for physical accessibility
  - Simple interaction for technical accessibility
  - Support for various literacy levels
- 🌐 **Digital Inclusion**:
  - No technical expertise required
  - Guidance for digital tasks
  - Bridge for technology gaps

## Prerequisites

- Python 3.10 or higher
- CUDA-capable GPU (for optimal performance)
- Internet connection
- Microphone for voice commands

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/malexandersalazar/casey.git
cd casey
```

2. **Create a virtual environment**
```bash
python -m venv venv
```

3. **Activate the virtual environment**

Windows:
```bash
.\venv\Scripts\activate
```

Unix/MacOS:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**

Create a `.env` file in the project root:
```env
APP_LANG=en
GROQ_API_KEY=your_value
GROQ_INTERACTION_MODEL_ID=llama-3.3-70b-versatile
GROQ_NOTIFICATION_MODEL_ID=llama-3.1-8b-instant
BING_API_KEY=your_value
VECTARA_API_KEY=your_value
TELEGRAM_API_TOKEN=your_value
TELEGRAM_CHAT_ID=your_value
IMGFLIP_USERNAME=your_value
IMGFLIP_PASSWORD=your_value
AZURE_OPENAI_API_KEY=your_value
AZURE_OPENAI_ENDPOINT=your_value
RUNWAYML_API_SECRET=your_value
```

## Usage

1. **Start the agent**
```bash
python program.py
```

2. **Initial setup**
- Configure your Telegram bot for notifications
- Test your microphone setup
- Verify API connections

3. **Basic voice commands**
```
"Create an article about [topic]"
"Make a social media post about [topic]"
"Generate an image of [description]"
"Create a meme about [topic]"
"Make a video showing [description]"
```

## System Requirements

### Minimum Requirements
- CPU: Intel i7/AMD Ryzen 7 or higher
- RAM: 32GB
- GPU: NVIDIA GPU with 16GB VRAM

### Recommended Requirements
- CPU: Intel i9/AMD Ryzen 9 or higher
- RAM: 64GB
- GPU: NVIDIA GPU with 24GB VRAM

## Technical Stack

Full dependencies are listed in `requirements.txt`

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

## Project Structure

```
└── casey
    ├── docs
    │   ├── capabilities
    │   │   └── memories
    │   ├── diagrams
    │   │   ├── memories
    │   │   └── workflows
    │   ├── screenshots
    │   └── workflows
    └── src
        ├── .venv
        ├── app
        │   ├── application
        │   └── client
        │       ├── data
        │       │   ├── captured_emotions
        │       │   └── transcripts
        │       ├── templates
        │       └── wwwroot
        │           ├── models
        │           └── scripts
        ├── data
        │   ├── clean
        │   │   ├── knowledge
        │   │   │   └── psychology
        │   │   │       └── es
        │   │   └── news
        │   │       └── en
        │   └── raw
        │       ├── library
        │       │   └── psychology
        │       │       └── es
        │       └── news
        └── notebooks
            └── images
```

## Documentation

Detailed documentation is available in the `docs` folder:
- [Workflow Documentation](./docs/workflows)
- [Architecture Diagrams](./docs/diagrams)

## Real-World Potential Use Cases

1. **Healthcare Professionals**
   - Updating patient records while maintaining sterile conditions
   - Creating medical documentation during procedures
   - Recording and organizing clinical observations hands-free
   - Quick access to medical references during consultations

2. **Vulnerable Populations**
   - Access to mental wellbeing support without requiring healthcare insurance
   - Support for those who cannot afford traditional therapy
   - Assistance for people in areas with limited mental health resources
   - Regular emotional support for isolated individuals
   - Guidance during personal crisis when immediate professional help isn't available

3. **Digital Inclusion**
   - Support for people with limited tech literacy
   - Voice-based assistance for those unfamiliar with computers
   - Help creating emails and managing online tasks for the digitally inexperienced
   - Guidance through basic digital operations without requiring technical knowledge

4. **Educational Support**
   - Companionship for children during remote learning
   - After-school support when parents are working
   - Homework assistance and educational conversations
   - Safe space for questions and learning for curious minds
   - Support for elderly learning new skills

5. **Accessibility Users**
   - Full content creation capabilities through voice
   - Platform-independent content management
   - Automated multi-format adaptation
   - Support for users with motor limitations
   - Assistance for visually impaired users

6. **Content Creators & Professionals**
   - Managing social media while performing other tasks
   - Creating content during live events
   - Multitasking during content production
   - Hands-free documentation and note-taking
   - Real-time content adaptation for different platforms

7. **Elderly Care**
   - Daily companionship for isolated seniors
   - Medication reminders and health tracking
   - Mental stimulation through conversations
   - Connection to digital services without technical barriers
   - Regular check-ins and emotional support

8. **Rural Communities**
   - Access to knowledge and support in remote areas
   - Bridge for digital services in areas with limited infrastructure
   - Educational support where resources are scarce
   - Cultural and linguistic adaptation for local contexts

9. **Family Support**
   - Companionship for children when parents are working
   - Educational support for families with limited resources
   - Safe space for teenagers to discuss concerns
   - Support for single-parent households
   - Assistance for caregivers

10. **Crisis Support**
    - 24/7 availability for emotional support
    - Immediate response during anxiety or panic episodes
    - Guided breathing and calming exercises
    - Connection to emergency services when needed
    - Consistent support during recovery periods

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Casey in your research, please cite:
```bibtex
@software{casey,
  author = {Salazar, Alexander},
  title = {Casey: Voice-Activated AI Companion for Mental Wellbeing & Content Creation},
  year = {2024},
  url = {https://github.com/malexandersalazar/casey}
}
```