import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sys
import os

# Add root directory to path to find core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.auth import RiotAuth
from core.store import ValorantStore
from core.assets import AssetManager

# --- Global State ---
auth_client = RiotAuth()
asset_manager = AssetManager()

# --- FastAPI App ---
app = FastAPI()

# Get absolute path to the directory containing this file
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")
templates_dir = os.path.join(base_dir, "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

class LoginRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/login")
async def login(req: LoginRequest):
    success, error = auth_client.extract_tokens_from_url(req.url)
    if not success:
        raise HTTPException(status_code=401, detail=error)
    return {"message": "Login successful"}

@app.get("/api/store")
async def get_store():
    if not auth_client.access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    store = ValorantStore(auth_client)
    store_data = store.get_storefront()
    
    if not store_data:
        raise HTTPException(status_code=500, detail="Failed to fetch store")

    # Fetch Prices
    price_map = {}
    store_offers = store_data.get("SkinsPanelLayout", {}).get("SingleItemStoreOffers", [])
    
    for offer in store_offers:
        offer_id = offer.get("OfferID")
        cost = offer.get("Cost", {}).get("85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741")
        if offer_id and cost:
            price_map[offer_id] = cost

    offers = store_data.get("SkinsPanelLayout", {}).get("SingleItemOffers", [])
    items = []
    
    for uuid in offers:
        skin_info = asset_manager.get_skin_data(uuid)
        price = price_map.get(uuid, "???")
        
        items.append({
            "uuid": uuid,
            "name": skin_info["name"],
            "icon": skin_info["icon"],
            "price": price
        })
        
    return {"items": items}

def start_server():
    # Paths to certs in root directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    cert_path = os.path.join(root_dir, "cert.pem")
    key_path = os.path.join(root_dir, "key.pem")

    if os.path.exists(cert_path) and os.path.exists(key_path):
        print(f"Starting Web Server on HTTPS (0.0.0.0:8000)...")
        uvicorn.run(app, host="0.0.0.0", port=8000, ssl_certfile=cert_path, ssl_keyfile=key_path)
    else:
        print("Warning: SSL certs not found. Starting on HTTP (0.0.0.0:8000)...")
        uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server()
