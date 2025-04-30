# this file name is given by gpt
import time
import requests
from fastapi import FastAPI, Request, Depends
from starlette.middleware.sessions import SessionMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import threading
import httpx  # to call external API

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecurekey123", session_cookie="chat_session")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.chatDB
chat_collection = db.chat_history
chat_collection.insert_one({"test": "checking if MongoDB works"})

# Inactivity timeout (5 minutes)
SESSION_TIMEOUT = 300  # 300 seconds = 5 minutes

# AI Chat API Endpoint (Change if needed)
AI_API_URL = "http://127.0.0.1:8004/chat"


async def get_rag_context(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8001/menu/{query}")  # Changed port to 8001
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                docs = data["results"]
                return "\n".join([f"- {doc['document']} (score: {doc['score']:.2f})" for doc in docs])
    return ""


### 🟢 1️⃣ Start a New Session
@app.get("/start_session/")
async def start_session(request: Request):
    request.session["user_id"] = str(time.time())  # Unique session ID
    request.session["chat_history"] = []  # Store user chat
    request.session["last_activity"] = time.time()
    
    # Start monitoring inactivity
    threading.Thread(target=check_session_timeout, args=(request,)).start()
    
    return {"message": "Session started", "user_id": request.session["user_id"]}





@app.post("/send_message/")
async def send_message(request: Request, user_message: str):
    if "user_id" not in request.session:
        return {"error": "No active session. Start a new session."}

    request.session["last_activity"] = time.time()

    # Get chat history or start a new one
    chat_history = request.session.get("chat_history", [])
    chat_history.append({"user": user_message})

    # --- Get RAG context ---
    rag_context = await get_rag_context(user_message)
    if rag_context:
        rag_prompt = f"Retrieved Context:\n{rag_context}\n\n"
    else:
        rag_prompt = ""

    # Format full prompt for LLaMA
    conversation = "\n".join(
        f"User: {m['user']}\nBot: {m.get('bot', '')}".strip()
        for m in chat_history
    )
    full_prompt = rag_prompt + conversation

    # Call your LLaMA model with retrieved context
    bot_response = get_ai_response(full_prompt)

    # Save bot reply to history
    chat_history[-1]["bot"] = bot_response
    request.session["chat_history"] = chat_history

    return {"user": user_message, "bot": bot_response}



### 🔴 3️⃣ End Session & Save Chat History
@app.get("/end_session/")
async def end_session(request: Request):
    if "user_id" not in request.session:
        return {"error": "No active session to end."}

    user_id = request.session["user_id"]
    chat_history = request.session["chat_history"]

    # Save chat history to MongoDB
    chat_collection.insert_one({
        "user_id": user_id,
        "chat_history": chat_history,
        "session_end": time.time()
    })

    # Clear session
    request.session.clear()
    
    return {"message": "Session ended and chat history saved."}


### ⏳ 4️⃣ Check Inactivity & Auto-Save Chat
def check_session_timeout(request: Request):
    user_id = request.session.get("user_id")
    while user_id in request.session:
        time.sleep(10)  # Check every 10 seconds
        last_activity = request.session.get("last_activity", time.time())

        if time.time() - last_activity > SESSION_TIMEOUT:
            print(f"Session timeout for user {user_id}, saving chat history...")
            end_session(request)
            break


### 🤖 5️⃣ Call AI API (LLaMA) for Response
def get_ai_response(user_query: str) -> str:
    try:
        print("get_ai_response function is called.")
        response = requests.post(AI_API_URL, json={"user_query": user_query}, stream=True)
        if response:
            print("response came")
        bot_response = "".join(chunk.decode() for chunk in response.iter_content(chunk_size=1024))
        return bot_response
    except Exception as e:
        return "Error connecting to AI API."
    















