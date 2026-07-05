#Om Namo Venketesaya

import time
from collections import deque #dequeu is higlhy optimised for speed
import matplotlib.pyplot as plt
import pandas as pd

from Market import testMarket
from detector import Velocity, Accelearation

window_size = 375 #5minutiions

df = pd.read_csv("nifty_last_7_days.csv")
df["date"] = pd.to_datetime(df["date"],dayfirst=True)
df = df[
    df["date"].dt.date == pd.Timestamp("2025-07-21").date()
]

prices = deque(maxlen=window_size)
velocity_detector = Velocity()
acceleration_detector = Accelearation()


fig, ax = plt.subplots(figsize=(14,6))

line, = ax.plot([], [], linewidth=2)

ax.set_title("Test Live Market")
ax.set_xlabel("Ticks")
ax.set_ylabel("Price")
ax.grid(True)

c = 0
n = 0

vvals = []

alert_x = []
alert_y = []

accel_x = []
accel_y = []

for _, row in df.iterrows():
    price = row["close"]


    prices.append(price)

    velocity = velocity_detector.calc(prices)
    acceleration = acceleration_detector.calc(velocity)

    if velocity is not None:
        vvals.append(velocity)


    line.set_xdata(range(len(prices)))
    line.set_ydata(prices)
    ax.scatter(alert_x, alert_y, color="red", s=50)
    ax.scatter(accel_x, accel_y,
           color="green",
           s=50)
    
    ax.relim()
    ax.autoscale_view()



    if velocity is not None and (velocity < -2 or velocity > 5):
        alert_x.append(len(prices) - 1)
        alert_y.append(price)

        print(
            f"{row['date']} | "
            f"Price: {price:.2f} | "
            f"Velocity: {velocity:.2f}"
        )
        c += 1


    if acceleration is not None and abs(acceleration) > 1:

        accel_x.append(len(prices)-1)
        accel_y.append(price)

        print(
            f"{row['date']} | "
            f"Acceleration: {acceleration:.2f}"
        )
        n += 1
    

print(c,n )
vvals = sorted(vvals)

line.set_xdata(range(len(prices)))
line.set_ydata(prices)

ax.scatter(alert_x, alert_y, color="red", s=50)

ax.relim()
ax.autoscale_view()

plt.show()