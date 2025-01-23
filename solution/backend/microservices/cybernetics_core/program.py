from containers import Container
from settings import AppSettings

from app import create_app

from seeders import SystemPromptSeeder

def configure():
    SystemPromptSeeder().seed()

def main():
    container = Container()
    configure()

    app = create_app(container)

    app_settings = AppSettings.from_env()

    logging_service = container.logging_service()
    logging_service.info(f"Starting app in {app_settings.APP_ENV} environment")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app_settings.APP_ENV == "development",
    )

if __name__ == "__main__":
    main()
