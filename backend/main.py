from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.chatbot import WeedChatbot

app = FastAPI(title="Weed Guide Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = WeedChatbot()


class ChatState(BaseModel):
    awaiting: str | None = None
    category: str | None = None
    selected_species: str | None = None


class ChatRequest(BaseModel):
    message: str
    state: ChatState | None = None


class ChatResponse(BaseModel):
    reply: str
    state: ChatState | None = None


@app.post("/api/chat")
async def chat(req: ChatRequest):
    state = req.state.model_dump() if req.state else None
    result = chatbot.process_message(req.message, state)
    return ChatResponse(**result)
