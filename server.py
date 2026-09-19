# Om Namo Venketesaya

import asyncio
import json
from datetime import datetime
import yfinance as yf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from collections import deque

from detector import EventDetector, Velocity


detector = EventDetector()
velocity_engine = Velocity(lookback=15)
price_history = deque(maxlen=400)
daily_points = deque(maxlen=400)
daily_anomalies = []
connected_clients = []
current_trading_date = None
last_processed_time = None

def reset_daily_state(new_date):

    global current_trading_date, detector
    current_trading_date = new_date
    price_history.clear()
    daily_points.clear()
    daily_anomalies.clear()
    detector = EventDetector()
    print(f"[*] Daily state reset for trading session: {new_date}")

def process_point(raw_close_val, timestamp_val):

    price = float(raw_close_val.iloc[0] if hasattr(raw_close_val, 'iloc') else raw_close_val) #extracts the value and gets the point
    time_str = str(timestamp_val.time())[:8] #converts the timestamp to str

    price_history.append(price)
    velocity = velocity_engine.calc(price_history) #this passes it onto the velcotiy clauclator
    alert = detector.update(abs(velocity)) if velocity is not None else False

    payload = {
        "time": time_str,
        "price": price,
        "confidence": round(detector.confidence, 2),
        "alert": alert
    }

    daily_points.append(payload)
    if alert:
        daily_anomalies.append(payload)

    return payload

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(stream_live_market()) #run this when the app is on
    yield
    task.cancel() #run this when the server is shutting down

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def get_homepage():
    return FileResponse("index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        if daily_points: #if theres ealier points noted
            is_weekend = datetime.now().weekday() >= 5
            await websocket.send_text(json.dumps({
                "type": "history",
                "date": current_trading_date.strftime("%A, %B %d, %Y") if current_trading_date else "Loading...",
                "is_weekend": is_weekend,
                "points": list(daily_points),
                "anomalies": list(daily_anomalies)
            }))
        
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def stream_live_market():
    global current_trading_date, last_processed_time
    while True:

        try:
            ticker_data = yf.download("^NSEI", period="1d", interval="1m", progress=False)
            if not ticker_data.empty:
                last_price_date = ticker_data.index[-1].date()
                current_candle_time = ticker_data.index[-1]

            if current_trading_date != last_price_date:
                reset_daily_state(last_price_date)

            if len(daily_points) == 0: #if the server booted mid day to display the existing points in the grpah
                for idx, row in ticker_data.iterrows():
                    process_point(row['Close'], idx)

                last_processed_time = current_candle_time
                print(f"[*] Catch-up complete. Anomalies found: {len(daily_anomalies)}")

            else:
                if current_candle_time != last_processed_time:
                        
                    latest_point = process_point(
                        ticker_data['Close'].iloc[-1], 
                        ticker_data.index[-1]
                    )

                    payload = json.dumps({"type": "tick", **latest_point})
                    print(f"[{latest_point['time']}] Live Price: {latest_point['price']} | Alert: {latest_point['alert']}")

                    for client in connected_clients:
                        await client.send_text(payload)
        except  Exception as e:
            print("Erro, ", e)

        await asyncio.sleep(60)


# run uvicorn server:app --reload in terminal to start up server locally