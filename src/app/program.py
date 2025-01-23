import os
import time
import subprocess

from dotenv import load_dotenv

from client import CaseyListenAndTalks
from logic import (
    InteractionManager,
    TelegramService,
    NewsService,
    VectaraService,
    ImgflipService,
    OpenAIService,
    RunwayService
)
from logic import (
    SemanticMemoryModule
)

load_dotenv(override=True)


def run_casey_see():
    subprocess.Popen(
        [r"C:\Windows\System32\cmd.exe", f"/K python client/viewer.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    time.sleep(1)  # Give Flask a second to start
    subprocess.Popen(
        [r"C:\Windows\System32\cmd.exe", f"/K python client/viewer_frontend.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

def run_casey_listen_and_talks():
    news_service = NewsService(os.environ.get("BING_API_KEY"))
    vectara_service = VectaraService(os.environ.get("VECTARA_API_KEY"))
    open_ai_service = OpenAIService(
        os.environ["AZURE_OPENAI_API_KEY"], os.environ["AZURE_OPENAI_ENDPOINT"]
    )
    imgflip_service = ImgflipService(
        os.environ.get("IMGFLIP_USERNAME"), os.environ.get("IMGFLIP_PASSWORD")
    )
    telegram_service = TelegramService(
        os.environ.get("TELEGRAM_API_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    )
    runway_service = RunwayService(os.environ.get('RUNWAYML_API_SECRET'))

    semantic_memory_module = SemanticMemoryModule(os.environ.get("GROQ_API_KEY"), os.environ.get("GROQ_INTERACTION_MODEL_ID"), vectara_service)

    interaction_manager = InteractionManager(
        os.environ.get("GROQ_API_KEY"),
        os.environ.get("GROQ_INTERACTION_MODEL_ID"),
        os.environ.get("GROQ_NOTIFICATION_MODEL_ID"),
        telegram_service,
        news_service,
        vectara_service,
        imgflip_service,
        open_ai_service,
        runway_service,
        semantic_memory_module
    )

    casey_listen = CaseyListenAndTalks(
        os.environ.get("APP_LANG"), interaction_manager, 120, os.environ.get("AZURE_SPEECH_SUBSCRIPTION_KEY")
    )
    casey_listen.run()


if __name__ == "__main__":
    run_casey_see()
    run_casey_listen_and_talks()
