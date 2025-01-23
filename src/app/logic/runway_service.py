import time
from runwayml import RunwayML


class RunwayService:
    """
    A service class for interacting with RunwayML's API to generate videos from images and text prompts.

    This class provides methods to create and retrieve AI-generated videos using RunwayML's
    image-to-video generation capabilities. It handles the asynchronous nature of video
    generation by providing methods to both initiate generation and poll for results.

    Attributes:
        api_secret (str): API secret key for authenticating with RunwayML services.
        runway_ml_client (RunwayML): Instance of RunwayML client for API interactions.

    Example:
        ```python
        service = RunwayService(api_secret="your_secret_key")
        
        # Start video generation
        task_id = service.create_video(
            prompt_image=image_data,
            prompt_text="A serene lake with rippling water"
        )
        
        # Retrieve the generated video
        video_url = service.retrieve_video(task_id)
        ```
    """
    def __init__(self, api_secret: str):
        self.api_secret = api_secret
        self.runway_ml_client = RunwayML(api_key=api_secret)

    def create_video(self, prompt_image, prompt_text: str) -> str:
        task = self.runway_ml_client.image_to_video.create(
            model="gen3a_turbo", prompt_image=prompt_image, prompt_text=prompt_text
        )
        return task.id

    def retrieve_video(self, task_id) -> str:
        """
        Poll for the video generation result and return the output URL when ready.

        Args:
            client: RunwayML client instance
            task_id: ID of the video generation task

        Returns:
            str: URL of the generated video when complete
        """
        while True:
            # Check the status of the generation
            result = self.runway_ml_client.tasks.retrieve(id=task_id)

            if result.status == "SUCCEEDED":
                return result.output[0]
            elif result.status == "FAILED":
                raise Exception("Video generation failed")
            elif result.status in ["PENDING", "RUNNING"]:
                print("Still processing runway video...")
                time.sleep(5)
            else:
                raise Exception(f"Unknown status: {result.status}")
