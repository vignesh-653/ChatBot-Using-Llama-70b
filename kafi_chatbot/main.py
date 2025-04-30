# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates

# app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# @app.get("/", response_class=HTMLResponse)
# async def serve_chat_ui(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request  # Ensure Request is imported
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import websockets

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# WebSocket connection to handle chat communication
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            user_message = await websocket.receive_text()  # Get message from user
            print(f"Received user message in main.py: {user_message}")
            
            # Send user message to chat terminal and get bot response
            bot_reply = await send_to_chat_terminal(user_message)
            
            # Send the bot reply back to the webpage
            await websocket.send_text(bot_reply)
    except WebSocketDisconnect:
        print("Client disconnected")

# Serve chat UI
@app.get("/", response_class=HTMLResponse)
async def serve_chat_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Function to communicate with chat terminal (reused from previous code)
# async def send_to_chat_terminal(user_input: str):
#     # This function will interact with your chat terminal code
#     # Modify this to connect to the terminal or API that handles the chatbot logic
#     import requests

#     BASE_URL = "http://127.0.0.1:8010"
#     response = requests.post(f"{BASE_URL}/send_message/", params={"user_message": user_input})
#     bot_reply = response.json().get("bot", "{}")
#     return bot_reply  # Return the bot's response

async def send_to_chat_terminal(user_input: str):
    uri = "ws://localhost:8765"  # WebSocket server for chat terminal
    async with websockets.connect(uri) as websocket:
        await websocket.send(user_input)  # Send the message to the server

        # Receive the bot's reply
        bot_reply = await websocket.recv()  # Wait for the response from the WebSocket server
        return bot_reply  # Return the bot's response