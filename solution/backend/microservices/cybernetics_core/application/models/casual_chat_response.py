from pydantic import Field, BaseModel


class CasualChatResponse(BaseModel):
    content: str = Field(..., description="The assistant text response")
    emotion: str = Field(..., description='The emotion that match the response content, must be one of: neutral, joy, sadness, surprise, anger, surprise, fear, and disgust')
