#Om Namo Venketesaya

import asyncio
import json
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from detector import EventDetector


@asynccontextmanager 
async def lifespan(app: FastAPI):
    # This runs on startup
    task = asyncio.create_task(replay_market()) #as soon as conecton made for startup send this function
    yield # The server runs here
    # This runs on shutdown
    task.cancel()


app = FastAPI(lifespan=lifespan) #the actual server
detector = EventDetector()
connected_clients = [] #list of connected clinets

temp_html = """
<!DOCTYPE html>
<html>
    <head><title>Nifty Live</title></head>
    <body>
        <h1>Nifty Live Event Stream</h1>
        <ul id="messages"></ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var data = JSON.parse(event.data);
                // We add visual flair if an alert is triggered
                if (data.alert) {
                    message.innerHTML = `<b>[${data.time}] 🚨 NIFTY: ${data.price} | Conf: ${data.confidence} | ALERT!</b>`;
                    message.style.color = "red";
                } else {
                    message.innerText = `[${data.time}] NIFTY: ${data.price} | Conf: ${data.confidence}`;
                }
                messages.appendChild(message);
            };
        </script>
    </body>
</html>
"""


@app.get("/") #the website sends get request so when the client opens the default url
async def get_homepage():
    return HTMLResponse(temp_html) # return the html page

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
    df = pd.read_csv("nifty_june_2025.csv")
    
    # Loop through the CSV row by row
    for index, row in df.iterrows():
        try:
            # Extract timestamp and close price
            raw_time = str(row['date'])
            current_price = float(row['close'])
            
            # Feed the algorithm
            alert_triggered = detector.update(current_price)

            payload = {
                "time" : raw_time.split(" ")[1],
                "price" : current_price,
                "confidence" : round(detector.confidence, 2),
                "alert" : alert_triggered
            } #the dict that will be sent accross as JSON

            json_payload = json.dumps(payload)

            for client in connected_clients:
                await client.send_text(json_payload) #send the payload to all connections

        except Exception as e:
            print(f"Error processing row: {e}")
            
        # Wait 1 second between ticks instead of 1 minute!
        await asyncio.sleep(1)