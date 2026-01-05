from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from services.ia import simple_chatbot_reply

router = APIRouter(prefix="/api/chat", tags=["chatbot"])


class ChatIn(BaseModel):
    message: str = ""


class ChatOut(BaseModel):
    reply: str


@router.post("", response_model=ChatOut)
def chat(payload: ChatIn):
    return ChatOut(reply=simple_chatbot_reply(payload.message))
