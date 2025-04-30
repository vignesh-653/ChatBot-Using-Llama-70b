from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from together import Together
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=api_key)

# API URLs for the agents
ORDER_AGENT_URL = "http://127.0.0.1:8002/order"
RECOMMENDATION_AGENT_URL = "http://127.0.0.1:8003/recommend"

# FastAPI App
app = FastAPI()

class ChatRequest(BaseModel):
    user_query: str



from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import requests

app = FastAPI()

def generate_chatbot_response(user_query):
    """Uses Together's API to generate chatbot responses with streaming (single string prompt format)."""
    import json

    full_prompt = f'''
"role": "system",
"content": (
    "You are a friendly coffee shop assistant. Always reply as a JSON with two keys:\\n"
    "retrieved context (rag) gives what similar items present in the menu to the user query. so if there is no exact item user asked, then suggest one or two items based rag context"
    "1. 'response': A helpful, concise reply to the user.\\n"
    "2. 'entities': A list of coffee or menu items mentioned (e.g., 'latte', 'croissant').\\n"
    "Only extract specific drink or food items, not names or locations.\\n"
    "Example format:\\n"
    "{{\\n"
    '  "response": "Our Jamaican Coffee River is a popular choice. Would you like it black or with cream?",\\n'
    '  "entities": ["Jamaican Coffee River"]\\n'
    "}}"
)

user: {user_query}
'''

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[{"role": "user", "content": full_prompt}], 
        max_tokens=150,
        temperature=0.6,
        top_p=0.5,
        top_k=30,
        stream=True  # Streaming enabled
    )

    async def token_stream():
        for token in response:
            if hasattr(token, 'choices') and token.choices:
                delta = token.choices[0].delta
                if delta and hasattr(delta, "content") and delta.content:
                    yield delta.content  # Send token as soon as it's generated

    return StreamingResponse(token_stream(), media_type="text/plain")

@app.post("/chat")
async def chatbot_assistant(request: dict):
    user_query = request["user_query"].strip().lower()
    print("chatbot is running properly")
    return generate_chatbot_response(user_query)
