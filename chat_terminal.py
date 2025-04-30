# import requests
# import json
# session = requests.Session()  # Use a persistent session

# BASE_URL = "http://127.0.0.1:8010"
# RECOMMEND_URL = "http://localhost:8003/recommend/"

# def get_recommendations(entities):
#     try:
#         rec_response = session.post(RECOMMEND_URL, json=entities)
#         if rec_response.status_code == 200:
#             rec_data = rec_response.json()
#             if rec_data.get("status") == "success":
#                 return rec_data.get("recommended_items", [])
#     except Exception as e:
#         print("Error calling recommendation agent:", e)
#     return []

# # Start session
# response = session.get(f"{BASE_URL}/start_session/")  # Use session instead of requests.get
# session_data = response.json()
# print("Session started:", session_data)

# count = 0
# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         break

#     try:
#         print("Sending request to FastAPI...", flush=True)
#         response = session.post(f"{BASE_URL}/send_message/", params={"user_message": user_input})
#         print("Response status:", response.status_code, flush=True)
        
#         bot_reply = response.json()
#         print("my bot reply:\n", bot_reply)

#         # Fix: parse the inner JSON string from the "bot" field
#         bot_data_str = bot_reply.get("bot", "{}")  # This is a string
#         data = json.loads(bot_data_str)  # Convert string to dict

#         # Extract bot message and entities
#         bot_message = data.get("response", "Error in response")
#         entities = data.get("entities", [])

#         print("my bot reply: ", bot_message)


#         if entities and count == 0:
#             recommendations =  get_recommendations(entities[:2])
#             print("Extracted entities: ", entities)
#             print("Recommended for you : ", recommendations)
#             count+=1


#     except Exception as e:
#         print("Request failed:", str(e), flush=True)

# # End session
# session.get(f"{BASE_URL}/end_session/")  # Use session.get
# print("Session ended.") 



import requests
import json
import websockets
import asyncio

BASE_URL = "http://127.0.0.1:8010"
RECOMMEND_URL = "http://localhost:8003/recommend/"

# Use a persistent session for chat terminal
session = requests.Session()

# Function to get recommendations
def get_recommendations(entities):
    try:
        rec_response = session.post(RECOMMEND_URL, json=entities)
        if rec_response.status_code == 200:
            rec_data = rec_response.json()
            if rec_data.get("status") == "success":
                return rec_data.get("recommended_items", [])
    except Exception as e:
        print("Error calling recommendation agent:", e)
    return []

# Start session
def start_session():
    try:
        response = session.get(f"{BASE_URL}/start_session/")
        session_data = response.json()
        print("Session started:", session_data)
    except Exception as e:
        print("Error starting session:", e)

# End session
def end_session():
    try:
        session.get(f"{BASE_URL}/end_session/")
        print("Session ended.")
    except Exception as e:
        print("Error ending session:", e)

# Function to handle chat messages and communicate with FastAPI backend
# async def handle_chat_message(websocket, user_message):
#     try:
#         print(f"Received user message in chat terminal: {user_message}")

#         # Send message to FastAPI backend
#         response = session.post(f"{BASE_URL}/send_message/", params={"user_message": user_message})
#         print("Response status:", response.status_code)
        
#         # Parse the response
#         bot_reply = response.json()
#         bot_data_str = bot_reply.get("bot", "{}")  # This is a string
#         data = json.loads(bot_data_str)  # Convert string to dict

#         # Extract bot message and entities
#         bot_message = data.get("response", "Error in response")
#         entities = data.get("entities", [])

#         print("Bot message:", bot_message)

#         # If entities are present, get recommendations
        
#         if entities and count == 0:
#             recommendations = get_recommendations(entities[:2])  # Get a maximum of 2 entities for recommendations
#             print("Extracted entities:", entities)
#             print("Recommended for you:", recommendations)
#             bot_message += "\nRecommended for you: " + str(recommendations)
#             count+=1

#         # Send bot's reply back to the WebSocket
#         await websocket.send(bot_message)
#     except Exception as e:
#         print("Error handling chat message:", e) 

# Function to handle chat messages and communicate with FastAPI backend
count = 0
async def handle_chat_message(websocket):
    global count 
    try:
        async for message in websocket:
            print(f"Received user message in chat terminal: {message}")

            # Send message to FastAPI backend
            response = session.post(f"{BASE_URL}/send_message/", params={"user_message": message})
            print("Response status:", response.status_code)
            
            # Parse the response
            bot_reply = response.json()
            bot_data_str = bot_reply.get("bot", "{}")  # This is a string
            data = json.loads(bot_data_str)  # Convert string to dict

            # Extract bot message and entities
            bot_message = data.get("response", "Error in response")
            entities = data.get("entities", [])

            print("Bot message:", bot_message)

            # If entities are present, get recommendations
            if entities and count == 0 :
                recommendations = get_recommendations(entities[:2])  # Get a maximum of 2 entities for recommendations
                print("Extracted entities:", entities)
                print("Recommended for you:", recommendations)
                bot_message += "\nRecommended for you: " + str(recommendations)
                count += 1

            # Send bot's reply back to the WebSocket
            await websocket.send(bot_message)
    except Exception as e:
        print("Error handling chat message:", e)

# WebSocket server to handle communication
async def chat_server():
    async with websockets.serve(handle_chat_message, "localhost", 8765):
        await asyncio.Future()  # Keep the server running


# Start the WebSocket server
if __name__ == "__main__":
    # Start the session when the chat terminal starts
    start_session()
    try:
        # Run the WebSocket server to handle messages
        asyncio.run(chat_server())
    finally:
        # Ensure that the session is ended when the server stops
        end_session()

