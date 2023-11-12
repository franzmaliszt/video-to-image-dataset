from pydantic import BaseModel


class SubmitModel(BaseModel):
    video: list[str] 
    images: list[str]
