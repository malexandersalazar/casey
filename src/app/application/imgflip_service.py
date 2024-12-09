import requests
from typing import Optional, Dict, List

class ImgflipService:
    """
    A service class for generating memes using the Imgflip API.
    Documentation: https://api.imgflip.com/
    """
    
    def __init__(self, username: str, password: str):
        """
        Initialize the meme generator service.
        
        Args:
            username: Imgflip username
            password: Imgflip password
        """
        self.base_url = "https://api.imgflip.com"
        self.username = username
        self.password = password

    def get_popular_memes(self, box_count: Optional[int] = None) -> List[Dict]:
        """
        Get a list of popular meme templates from Imgflip.
        
        Args:
            box_count: Optional filter for number of text boxes
            
        Returns:
            List of dictionaries containing meme template information
        """
        try:
            response = requests.get(f"{self.base_url}/get_memes")
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                memes = data["data"]["memes"]
                if box_count is not None:
                    memes = [meme for meme in memes if meme["box_count"] == box_count]
                return memes
            else:
                raise Exception(f"Failed to get memes: {data['error_message']}")
                
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def get_two_box_memes(self) -> List[Dict]:
        """
        Get a list of meme templates that have exactly two text boxes.
        
        Returns:
            List of dictionaries containing meme template information
        """
        return self.get_popular_memes(box_count=2)

    def create_meme(
        self,
        template_id: str,
        top_text: str,
        bottom_text: str,
        max_font_size: Optional[int] = None
    ) -> Dict:
        """
        Generate a meme using the specified template and two text boxes.
        
        Args:
            template_id: The ID of the meme template to use
            top_text: Text for the top box
            bottom_text: Text for the bottom box
            max_font_size: Optional maximum font size for the text
            
        Returns:
            Dictionary containing the URL of the generated meme
        """
        # Prepare the request payload
        payload = {
            "template_id": template_id,
            "username": self.username,
            "password": self.password,
            "boxes[0][text]": top_text,
            "boxes[1][text]": bottom_text
        }
        
        if max_font_size:
            payload["max_font_size"] = max_font_size

        try:
            response = requests.post(f"{self.base_url}/caption_image", data=payload)
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                return {
                    "url": data["data"]["url"],
                    "page_url": data["data"]["page_url"]
                }
            else:
                raise Exception(f"Failed to generate meme: {data['error_message']}")
                
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def find_template_by_name(self, name: str, two_boxes_only: bool = False) -> Optional[Dict]:
        """
        Find a meme template by name (case-insensitive partial match).
        
        Args:
            name: Name of the meme template to find
            two_boxes_only: If True, only return templates with exactly two text boxes
            
        Returns:
            Dictionary containing template information or None if not found
        """
        templates = self.get_two_box_memes() if two_boxes_only else self.get_popular_memes()
        name = name.lower()
        
        for template in templates:
            if name in template["name"].lower():
                return template
                
        return None

    def list_two_box_meme_names(self) -> List[str]:
        """
        Get a list of names of all available two-box meme templates.
        
        Returns:
            List of meme template names
        """
        templates = self.get_two_box_memes()
        return [template["name"] for template in templates]