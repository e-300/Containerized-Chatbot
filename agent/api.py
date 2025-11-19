from fastapi import FastAPI
from pydantic import BaseModel
from agent.claude import AnthropicAgent
import os
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

api_key = os.getenv("ANTHROPIC_API_KEY")

if api_key is None:
    raise ValueError("ANTHROPIC_API_KEY environment variable is missing.")

agent = AnthropicAgent(api_key=api_key, system_prompt=None)


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(req: ChatRequest):
    response = agent.process(req.message)
    #use agent?
    return {"response": response}



@app.get("/")
async def root():
    return {"message": "AI Agent API is running"}