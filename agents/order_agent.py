from fastapi import FastAPI
import requests

app = FastAPI()

MENU_AGENT_URL = "http://127.0.0.1:8001/menu"

@app.post("/order")
def order_item(order: dict):
    item = order.get("item", "").title()
    
    # Get item details from Menu Agent
    response = requests.get(f"{MENU_AGENT_URL}/{item}")
    menu_data = response.json()

    if menu_data["status"] == "success":
        return {"status": "success", "message": f"Order confirmed for {item}. Price: ${menu_data['price']}"}
    
    return {"status": "error", "message": f"{item} is not available in the menu."}
