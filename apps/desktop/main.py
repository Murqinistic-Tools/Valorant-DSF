import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import ssl
import threading
import webview
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.auth import RiotAuth
from core.store import ValorantStore
from core.assets import AssetManager

# --- Global State ---
auth_client = RiotAuth()
asset_manager = AssetManager()
main_window = None

# --- FastAPI App ---
app = FastAPI()

# Get absolute path to the directory containing this file
# Note: In PyInstaller, we might need sys._MEIPASS, but for now let's fix the dev environment
base_dir = os.path.dirname(os.path.abspath(__file__))

# Check if we are running in a bundle
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS

# The desktop app seems to expect static files in the same directory as main.py
# based on the original code `directory="static"`.
# However, looking at the file structure, we need to be sure where `static` is.
# Assuming it's in apps/desktop/static or similar.
static_dir = os.path.join(base_dir, "static")
templates_dir = os.path.join(base_dir, "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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

# --- Desktop API Bridge ---
class Api:
    def start_login(self):
        """
        Opens a new webview window for Riot Login and sniffs the URL for tokens.
        """
        login_url = "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token&nonce=1&scope=account%20openid"
        
        # Open the auth window
        auth_window = webview.create_window('Riot Login', login_url, width=1100, height=800)
        
        # Start sniffing in a separate thread to not block the UI
        threading.Thread(target=self._sniff_token, args=(auth_window,), daemon=True).start()

    def _sniff_token(self, window):
        max_attempts = 1200 # 2 minutes timeout (1200 * 0.1s)
        attempts = 0
        
        while attempts < max_attempts:
            try:
                current_url = window.get_current_url()
                if current_url and "access_token=" in current_url:
                    # Token found!
                    window.hide() # Ghost Close: Hide IMMEDIATELY
                    success, msg = auth_client.extract_tokens_from_url(current_url)
                    if success:
                        window.destroy()
                        # Notify Frontend
                        main_window.evaluate_js("window.dispatchEvent(new Event('login-success'));")
                        return
            except Exception as e:
                pass
            
            time.sleep(0.1)
            attempts += 1
        
        # If timeout or closed
        # window.destroy() # might be already closed

# --- Main Execution ---
def start_server():
    # SSL Context for self-signed certs (needed for some Riot APIs if we were proxying, 
    # but here we are just serving local content. HTTP is fine for localhost webview usually,
    # but let's keep HTTPS if we want to be safe or if previously configured).
    # Actually, for local webview, HTTP is faster and easier. Let's stick to HTTP for localhost.
    uvicorn.run(app, host="127.0.0.1", port=23456, log_level="error")

if __name__ == "__main__":
    # Start FastAPI in background thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # Create API Bridge
    api = Api()

    # Resolve Icon Path
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icon.ico'))

    # Create Main Window
    main_window = webview.create_window(
        'Valorant DSF', 
        'http://127.0.0.1:23456',
        width=700,
        height=400,
        resizable=False,
        background_color='#000000',
        js_api=api
    )

    webview.start(debug=False, icon=icon_path)
