from pydantic import BaseModel
from typing import Optional


class MessageCreate(BaseModel):
    message: str


class Message(BaseModel):
    message: str
    id: str
    process_time: Optional[float]

    class Config:
        from_attributes = True
