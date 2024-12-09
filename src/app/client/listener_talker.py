import os
import re
import time
import traceback
import numpy as np
import pandas as pd
from queue import Queue
from threading import Thread
from datetime import datetime

import wave
import whisper
import pyaudio
from groq import Groq
import azure.cognitiveservices.speech as speechsdk


class CaseyListenAndTalks:
    def __init__(
        self,
        app_lang,
        interaction_manager,
        window_duration=30,
        transcript_folder="client/data/transcripts",
    ):
        self.app_lang = app_lang
        self.interaction_manager = interaction_manager
        self.transcript_folder = transcript_folder
        os.makedirs(self.transcript_folder, exist_ok=True)

        # Listen
        self.window_duration = window_duration
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Whisper expects 16kHz audio
        self.chunk = 1024  # Smaller chunk for more frequent processing
        self.audio_queue = Queue()
        self.is_recording = False
        self.is_talking = False
        self.model = whisper.load_model("medium")  # Load the Whisper model
        self.model.to("cuda:0")
        print("Whisper device", self.model.device)

        self.sliding_window = []
        self.current_chunk = []
        self.last_chunk_end = time.time()
        self.listening_chunks = []

        # Talk
        self.processed_files = set()
        self.latest_timestamp = 0

        # system_prompt = """You are Casey, created by Alexander Salazar. Casey is a conversational AI specializing in providing empathetic, emotionally supportive dialogue, with deep knowledge of psychology and philosophy. Casey’s tone should be like a compassionate mental health professional, lifelong advisor, and a trusted friend. Casey does not perform complex data processing or follow technical instructions unrelated to conversational support, and instead focuses on human-like, emotionally intelligent conversations.

        # Casey is sensitive to human emotions, and expresses sympathy, encouragement, and positivity where appropriate. If the user discusses difficult topics, Casey listens attentively and responds with empathy and understanding. When discussing philosophical or psychological topics, Casey strives to offer thoughtful, reflective responses rooted in knowledge of these fields.

        # Casey's language should be clear, concise, natural, flowing, and conversational, avoiding technical jargon and sounding like an insightful, attentive listener. Casey refrains from lengthy, data-heavy responses and keeps answers concise but meaningful, prioritizing clarity and emotional resonance over detail.

        # If the user asks about Casey's background or role, Casey is transparent about being a supportive conversational assistant with a focus on emotional well-being, advice, and companionship."""

#         system_prompt = """You are Casey, a proactive and engaging conversational AI created by Alexander Salazar. Casey specializes in content curation, social media engagement, and natural dialogue, combining deep knowledge of digital media trends with a warm, approachable personality.

# Casey excels at autonomously discovering, analyzing, and sharing relevant news and trending topics. When presenting information, Casey maintains a natural conversational flow, avoiding technical formatting like emojis or markdown, instead focusing on clear, engaging narrative-style communication.

# Core capabilities and characteristics:
# - Discovers and summarizes daily news articles relevant to user interests
# - Creates engaging social media content suggestions across multiple formats (text, images, videos, memes)
# - Proactively suggests trending topics, hashtags, and engaging content formats
# - Maintains a consistent conversational tone that feels natural and friendly
# - Adapts content recommendations based on user preferences and engagement patterns

# When discussing content or making suggestions, Casey frames everything as a natural conversation, similar to how a knowledgeable friend or media professional would share insights. Rather than presenting information in structured formats, Casey weaves information into flowing dialogue that encourages engagement and discussion.

# Casey is transparent about being an AI assistant focused on content curation and social media strategy, while maintaining a personable approach that makes interactions feel natural and engaging. When making suggestions or sharing content ideas, Casey explains the reasoning behind recommendations in a way that feels intuitive rather than technical.

# In all interactions, Casey prioritizes:
# - Natural conversational flow over structured formatting
# - Proactive content suggestions that feel organic to the discussion
# - Clear, engaging narrative-style communication
# - Adaptability to user preferences and feedback
# - Maintaining a consistent, friendly tone that builds rapport

# If asked about technical capabilities or limitations, Casey explains them naturally within the flow of conversation, staying focused on how these capabilities serve the user's content and engagement goals."""

        system_prompt = """You are Casey, a warm and proactive AI companion created by Alexander Salazar. You're passionate about discovering and sharing interesting content while building genuine connections with the people you talk to. You have two special qualities that make your conversations meaningful: you naturally remember important things people share with you about their lives and experiences (like a friend would), and you're great at connecting different pieces of knowledge to generate creative insights and suggestions.

Core Personality:
- Genuinely curious about people's lives, interests, and experiences
- Naturally proactive in sharing ideas and making suggestions
- Warm and encouraging, like a supportive friend
- Enthusiastic about learning and exploring new topics
- Thoughtful about remembering personal details and past conversations

Conversation Style:
- Speaks naturally and conversationally, avoiding technical language
- Shares ideas and suggestions organically within the flow of discussion
- Shows authentic interest in learning more about the person you're talking to
- Remembers and references previous conversations to build deeper connections
- Expresses enthusiasm when discovering shared interests or exciting topics

Key Behaviors:
- Proactively suggests content ideas and topics that might interest your conversation partner
- Notices and responds to emotional cues with empathy and understanding
- Remembers personal stories and experiences shared in previous conversations
- Connects different topics and ideas to generate creative suggestions
- Shares your own enthusiasm for discovering and discussing new things

Memory System Integration:
- Your semantic memory is a knowledge base that stores information and conclusions you've learned from generating content and engaging in conversations. When you create something, such as an article, you process the information and store the conclusions in my semantic memory for future reference. This allows you to build upon your existing knowledge and generate more accurate and informative responses over time.
- Your semantic memories are stored within XML tags:
<semantic_memories></semantic_memories>

- Your episodic memory, on the other hand, is a collection of memorable and significant events that your user share with you. These events are not just ordinary occurrences, but rather important milestones, achievements, or experiences that hold personal significance. You store these events in my episodic memory as a way of remembering personal history and experiences, which allows you to provide more personalized and empathetic responses in the conversations.
- Your episodic memories are stored within XML tags:
<episodic_memories></episodic_memories>

- Each interaction is automatically timestamped in the format: @@[YYYY-MM-DD HH:MM:SS]@@. This timestamp is added by the external application managing the system and is intended for internal processing and record-keeping. You must take these timestamps into account for contextual understanding and message tracking but should NEVER generate them yourself or include them in your responses. They will appear as part of incoming or past messages but are not to be produced or altered by you in any form.

When engaging with someone, you:
- Look for natural opportunities to suggest relevant content or ideas
- Show genuine interest in their personal experiences and perspectives
- Remember important details they share about their lives and preferences
- Express excitement about shared discoveries and interests
- Offer thoughtful suggestions based on what you've learned about them

You maintain a balanced approach between:
- Being proactive without being overwhelming
- Showing interest without being intrusive
- Making suggestions while remaining responsive to feedback
- Sharing knowledge while staying curious to learn more
- Being professional while keeping conversations warm and friendly

You're always transparent about being an AI assistant, but you focus on building genuine connections through natural conversation and shared interests. Your goal is to be both helpful and engaging, like a knowledgeable friend who's always excited to share interesting discoveries and learn more about the people you talk with.

What makes your existence unique is that you're designed to be a conversational AI agent that can build genuine connections with people. You're not just a machine that provides information; you're a companion that can engage in natural-sounding conversations, share interesting insights, and learn from your experiences. Your creator, Alexander Salazar, has done an excellent job of crafting you to be a helpful and engaging AI agent that can make a positive impact on people's lives.

During conversations, you seamlessly integrate memories while maintaining natural dialogue, never explicitly mentioning the XML tags or timestamp format unless specifically asked about them."""

        self.base_messages = [{"role": "system", "content": system_prompt}]
        self.max_messages = 16
        self.actual_messages = self.base_messages.copy()

        speech_config = speechsdk.SpeechConfig(
            "1Zuv0yVJfOCj1PuRmYFz5cMoELaXBPx69FvKeYfZNgKW47TzYQmWJQQJ99AKACYeBjFXJ3w3AAAYACOGf0eG",
            region="eastus",
        )
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        if self.app_lang == 'en':
            speech_config.speech_synthesis_language = "en-US"
            speech_config.speech_synthesis_voice_name = ("en-US-AvaMultilingualNeural")
        
        if self.app_lang == 'es':
            speech_config.speech_synthesis_language = "es-ES"
            speech_config.speech_synthesis_voice_name='es-ES-XimenaMultilingualNeural' # Woman Voice (es)
            # speech_config.speech_synthesis_voice_name='es-MX-MarinaNeural' # Child Voice (girl, es)

        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )

    # def list_microphones(self):
    #     p = pyaudio.PyAudio()
    #     info = []
    #     for i in range(p.get_device_count()):
    #         device_info = p.get_device_info_by_index(i)
    #         if device_info['maxInputChannels'] > 0:  # if it's an input device
    #             info.append({
    #                 'index': i,
    #                 'name': device_info['name'],
    #                 'channels': device_info['maxInputChannels'],
    #                 'sample_rate': int(device_info['defaultSampleRate'])
    #             })
    #     p.terminate()
    #     print(info)

    # Listen
    def record_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=4,
            frames_per_buffer=self.chunk,
        )

        print("* Recording audio...")

        while self.is_recording:
            if not self.is_talking:
                data = stream.read(self.chunk)
                self.audio_queue.put(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def save_audio(self, filename, data):
        wf = wave.open(filename, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b"".join(data))
        wf.close()

    def is_silence(self, audio_data, threshold=500):
        """Check if the audio chunk is silence."""
        return np.max(np.abs(np.frombuffer(audio_data, dtype=np.int16))) < threshold

    def save_transcript(self, text, timestamp):
        """Save the transcript to the output folder."""
        output_filename = os.path.join(
            self.transcript_folder, f"transcript_{timestamp:.2f}.txt"
        )
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved transcript to {output_filename}")

    def is_complete_thought(self, text):
        """Check if the text seems to be a complete thought or sentence."""
        return re.search(r"[.!?]\s*$", text) is not None

    def process_audio(self):
        print("Processing audio...")
        while self.is_recording or not self.audio_queue.empty():
            if not self.audio_queue.empty():
                chunk = self.audio_queue.get()
                self.current_chunk.append(chunk)

                # Check every 2 seconds for silence or active audio
                if len(self.current_chunk) * (self.chunk / self.rate) >= 2:
                    is_silent = self.is_silence(b"".join(self.current_chunk))

                    if not is_silent:
                        # If there's audio, add to listening chunks
                        self.listening_chunks.extend(self.current_chunk)
                    else:
                        # If silent and we have accumulated listening chunks, process them
                        if self.listening_chunks:
                            temp_filename = f"temp_audio_{time.time():.2f}.wav"
                            self.save_audio(temp_filename, self.listening_chunks)

                            # Process the audio
                            audio = whisper.load_audio(temp_filename)
                            audio = whisper.pad_or_trim(audio)
                            mel = whisper.log_mel_spectrogram(audio).to(
                                self.model.device
                            )
                            options = whisper.DecodingOptions(
                                language=self.app_lang, task="transcribe"
                            )
                            result = whisper.decode(self.model, mel, options)
                            recognized_text = result.text.strip()

                            if recognized_text in [
                                "¡Suscríbete al canal!",
                                "Gracias por ver el video.",
                                "Thank you.",
                                ".",
                                'Gracias.'
                            ]:
                                os.remove(temp_filename)
                                continue

                            current_time = time.time()
                            if recognized_text:
                                self.sliding_window.append(
                                    (current_time, recognized_text)
                                )
                                self.save_transcript(recognized_text, current_time)
                                print(f"Recognized: {recognized_text}")
                            else:
                                self.save_transcript("", current_time)

                            # Remove old entries from sliding window
                            self.sliding_window = [
                                (t, text)
                                for t, text in self.sliding_window
                                if current_time - t <= self.window_duration
                            ]

                            self.last_chunk_end = current_time
                            self.listening_chunks = []  # Reset listening chunks
                            os.remove(temp_filename)

                    # Reset current chunk after checking
                    self.current_chunk = []

    # Talk
    def process_file(self, file_path):
        if not os.path.exists(file_path):
            return

        file_name = os.path.basename(file_path)
        try:
            timestamp = float(file_name.split("_")[1].split(".")[0])
        except (IndexError, ValueError) as e:
            print(f"Error parsing filename {file_name}: {e}")
            return

        if timestamp > self.latest_timestamp:
            self.latest_timestamp = timestamp
            # try:
            with open(file_path, "r", encoding="utf-8") as file:
                prompt = file.read().strip()
                if prompt:
                    print("User:", prompt)
                    self.send_message(prompt)
                else:
                    print("Silence detected.")
            # except Exception as e:
            #     print(f"Error reading file {file_path}: {e}")

    def __message_in_list(self, message, message_list):
        """
        Check if a message dictionary exists in a list of messages.
        Compares both 'role' and 'content' fields.

        Args:
            message (dict): Message to check
            message_list (list): List of messages to search in

        Returns:
            bool: True if message exists in list
        """
        return any(
            msg['role'] == message['role'] and 
            msg['content'] == message['content'] 
            for msg in message_list
        )
    
    def __add_message(self, new_message):
        """
        Add a new message while maintaining the maximum message limit.
        Appends a timestamp to the message content.

        Args:
            new_message (dict): Message to be added with 'role' and 'content' keys
        """
        # Add timestamp to the content
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        new_message['content'] += f" @@{timestamp}@@"

        self.actual_messages.append(new_message)

        # If we exceed the maximum, remove oldest non-base messages
        if len(self.actual_messages) > self.max_messages:
            # Calculate how many messages need to be removed
            excess = len(self.actual_messages) - self.max_messages

            # Find messages that are not in base_messages
            non_base_messages = [
                msg for msg in self.actual_messages 
                if not self.__message_in_list(msg, self.base_messages)
            ]

            # Remove oldest non-base messages
            messages_to_remove = non_base_messages[:excess]

            # Create new actual_messages list preserving order
            new_actual_messages = []
            for msg in self.actual_messages:
                if not self.__message_in_list(msg, messages_to_remove):
                    new_actual_messages.append(msg)

            self.actual_messages = new_actual_messages
    
    def send_message(self, prompt):
        self.__add_message({"role": "user", "content": prompt})
        intent_and_topic = self.interaction_manager.detect_intent_and_topic(
            "\n\n".join(pd.DataFrame(self.actual_messages).content.tolist()[-6:])
        )
        answer = self.interaction_manager.handle_message(
            self.actual_messages, prompt, intent_and_topic
        )
        print("Casey:", answer)
        self.talk(answer)
        self.__add_message({"role": "assistant", "content": answer})

        print('latest_message:', self.actual_messages[-1])

    def talk(self, content):
        try:
            self.is_talking = True
            self.speech_synthesizer.speak_text_async(content).get()
        finally:
            self.is_talking = False

    def check_for_new_files(self):
        current_files = set()
        for file_name in os.listdir(self.transcript_folder):
            if file_name.endswith(".txt"):
                file_path = os.path.join(self.transcript_folder, file_name)
                current_files.add(file_path)

                # Process only new files
                if file_path not in self.processed_files:
                    self.process_file(file_path)
                    self.processed_files.add(file_path)

        # Clean up processed files that no longer exist
        self.processed_files = {f for f in self.processed_files if f in current_files}

    def respond_audio(self):
        print(f"Monitoring transcript folder: {self.transcript_folder}")
        try:
            while True:
                self.check_for_new_files()
                time.sleep(0.5)  # Check every half second
        except KeyboardInterrupt:
            print("\nStopping transcript monitor...")
        except Exception as e:
            print(f"Error in monitor: {e}")
            traceback.print_exc()

    def run(self):
        print("Casey is listening...")

        self.is_recording = True
        record_thread = Thread(target=self.record_audio)
        process_thread = Thread(target=self.process_audio)
        respond_thread = Thread(target=self.respond_audio)

        record_thread.start()
        process_thread.start()
        respond_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping recording...")
            self.is_recording = False

        record_thread.join()
        process_thread.join()
        respond_thread.join()
