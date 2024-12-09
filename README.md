# Casey - Voice-Commanded AI Content Creation Agent

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

Casey is a voice-commanded AI agent that autonomously creates and manages multi-format content while keeping your hands free. It combines advanced language models, computer vision, and speech processing to enable hands-free content creation, making it ideal for professionals who need to multitask or require accessibility accommodations.

## Key Features

- 🎙️ **Voice-Commanded Operation**: Completely hands-free interaction
- 📰 **Multi-Format Content Creation**: Articles, social media posts, images, videos, and memes
- 🧠 **Dual Memory System**: Semantic and episodic memory for context-aware interactions
- 🔄 **Autonomous News Processing**: Automatic retrieval and analysis of relevant news
- 🎯 **Platform-Optimized Content**: Automatic adaptation for different social media platforms
- ♿ **Accessibility-First Design**: Fully operational through voice commands

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

## Dependencies

Major components:
- `groq`: LLM integration
- `openai`: DALL-E integration
- `runwayml`: Video generation
- `azure-cognitiveservices-speech`: Speech recognition
- `langchain`: Text processing
- `torch`: Machine learning operations

Full dependencies are listed in `requirements.txt`

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

## Common Use Cases

1. **Medical Professionals**
   - Updating patient records while maintaining sterile conditions
   - Creating medical documentation during procedures
   - Sharing research findings hands-free

2. **Content Creators**
   - Managing social media while performing other tasks
   - Creating content during live events
   - Multitasking during content production

3. **Accessibility Users**
   - Full content creation capabilities through voice
   - Platform-independent content management
   - Automated multi-format adaptation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Casey in your research, please cite:
```bibtex
@software{casey,
  author = {Salazar, Alexander},
  title = {Casey: Voice-Commanded AI Content Creation Agent},
  year = {2024},
  url = {https://github.com/malexandersalazar/casey}
}
```