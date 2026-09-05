#Om Namo Venketesaya

import asyncio
import json
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from detector import EventDetector, Velocity

@asynccontextmanager 
async def lifespan(app: FastAPI):
    # This runs on startup
    task = asyncio.create_task(replay_market()) #as soon as conecton made for startup send this function
    yield # The server runs here
    # This runs on shutdown
    task.cancel()


app = FastAPI(lifespan=lifespan) #the actual server


detector = EventDetector()
velocity_engine = Velocity(lookback=15) # Looks back 15 ticks to calculate speed
price_history = [] # Stores history for velocity math
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

async def replay_market():
    df = pd.read_csv("nifty_last_7_days.csv")
    
    # Loop through the CSV row by row
    for index, row in df.iterrows():
        try:

            raw_time = str(row['date'])
            current_price = float(row['close'])
            
            price_history.append(current_price)
            
            current_velocity = velocity_engine.calc(price_history)
            
            # 3. Feed the velocity magnitude (absolute value) to the detector
            if current_velocity is not None:
                alert_triggered = detector.update(abs(current_velocity))
            else:
                alert_triggered = False

            payload = {
                "time" : raw_time.split(" ")[1],
                "price" : current_price,
                "confidence" : round(detector.confidence, 2),
                "alert" : alert_triggered
            } #the dict that will be sent accross as JSON
            if current_velocity is not None:
                print(f"Vel: {abs(current_velocity):.2f} | Trigger need: >??? | Conf: {detector.confidence:.2f} | Notify need: >???")
            
            json_payload = json.dumps(payload)

            for client in connected_clients:
                await client.send_text(json_payload) #send the payload to all connections

        except Exception as e:
            print(f"Error processing row: {e}")
            
        # Wait 0.1 second between ticks instead of 1 minute!
        await asyncio.sleep(0.1)