#Om Namo Venketesaya
from itertools import product
from collections import deque
import pandas as pd

from detector import Velocity, Accelearation, Regression, EventDetector

window_size = 375
tolerance = 3
expectedTicks = [17,34,150,280,340]

df = pd.read_csv("nifty_last_7_days.csv") #reads csv
df["date"] = pd.to_datetime(df["date"],dayfirst=True) #converts each value form date colouns to objects of format dd / mm / yyyy
df = df[
    df["date"].dt.date == pd.Timestamp("2025-07-23").date()
] #filters to keep only required date

velocity_windows = [15, 20, 25, 30]
regression_windows = [15, 20, 25]

trigger_values = [2, 3, 4]
notify_values = [6, 8, 10]
decay_values = [0.80, 0.85, 0.90]

results = []

for vel_win, reg_win, trig, notify, decay in product(
    velocity_windows,
    regression_windows,
    trigger_values,
    notify_values,
    decay_values
):
    prices = deque(maxlen=window_size)

    velocity_detector = Velocity(lookback=vel_win)
    acceleration_detector = Accelearation()
    regression_detector = Regression(lookback=reg_win)

    event_detector = EventDetector(
        trigger=trig,
        notify=notify,
        decay=decay
    )

    events = 0
    event_ticks = []
    tick = 0

    for _, row in df.iterrows():

        tick += 1

        price = row["close"]

        prices.append(price)

        velocity = velocity_detector.calc(prices)
        acceleration = acceleration_detector.calc(velocity)
        gradient = regression_detector.calc(prices)

        score = (
            abs(velocity or 0)
            + abs(acceleration or 0)
            + abs(gradient or 0)
        )

        if event_detector.update(score):
            events += 1
            event_ticks.append(tick)

    total_error = 0

    for expected, detected in zip(expectedTicks, event_ticks):
        total_error += abs(expected - detected)

  
    total_error += abs(len(event_ticks) - len(expectedTicks)) * 100

  

    results.append({

        "error": total_error,
        "events": events,
        "ticks": event_ticks,

        "velocity_window": vel_win,
        "regression_window": reg_win,

        "trigger": trig,
        "notify": notify,
        "decay": decay

    })

results.sort(key=lambda x: x['error'])

if len(results) == 0:

    print("No parameter combination satisfied the tolerance.")

else:

    for rank, r in enumerate(results[:5], start=1):

        print(f"\nRank {rank}")
        print(r)