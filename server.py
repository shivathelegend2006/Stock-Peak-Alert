#Om Namo Venketesaya

import asyncio
import json
import pandas as pd
from datetime import datetime
import yfinance as yf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from collections import deque

from detector import EventDetector, Velocity

@asynccontextmanager 
async def lifespan(app: FastAPI):
    # This runs on startup
    task = asyncio.create_task(stream_live_market()) #as soon as conecton made for startup send this function
    yield # The server runs here
    # This runs on shutdown
    task.cancel()


app = FastAPI(lifespan=lifespan) #the actual server


detector = EventDetector()
velocity_engine = Velocity(lookback=15) # Looks back 15 ticks to calculate speed
price_history = deque(maxlen=400) # Stores history for velocity math
connected_clients = [] #list of connected clinets


@app.get("/") #the website sends get request so when the client opens the default url
async def get_homepage():
    return FileResponse("index.html") # return the html page

@app.websocket("/ws") #immediatly after the page loads the connecgttio is formed so run this function
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept() # wait for the client side to accept
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text() #check any mor requests follwing
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
async def stream_live_market():
    
    while True:
        try:
            
            ticker_data = yf.download("^NSEI", period="1d", interval="1m", progress=False)
            
            if not ticker_data.empty:
                
                raw_close = ticker_data['Close'].iloc[-1]
               
                latest_price = float(raw_close.iloc[0] if hasattr(raw_close, 'iloc') else raw_close)
                raw_time = str(ticker_data.index[-1].time())[:8] # just to get in proper format
                
                
                price_history.append(latest_price)
                current_velocity = velocity_engine.calc(price_history)
                
                if current_velocity is not None:
                    alert_triggered = detector.update(abs(current_velocity))
                else:
                    alert_triggered = False

                
                payload = {
                    "time" : raw_time,
                    "price" : latest_price,
                    "confidence" : round(detector.confidence, 2),
                    "alert" : alert_triggered
                } 

                json_payload = json.dumps(payload)
                print(f"[{raw_time}] Live Price: {latest_price} | Alert: {alert_triggered}")

               
                for client in connected_clients:
                    await client.send_text(json_payload) 

        except Exception as e:
            print(f"Error fetching live data: {e}")
            
        
        await asyncio.sleep(60)