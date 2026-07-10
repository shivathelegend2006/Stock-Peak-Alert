#Om Namo Venketesaya

import time
from collections import deque #dequeu is higlhy optimised for speed
import matplotlib.pyplot as plt
import pandas as pd


from detector import Velocity, Accelearation, Regression, EventDetector

window_size = 375 #5minutiions

df = pd.read_csv("nifty_last_7_days.csv") #reads csv
df["date"] = pd.to_datetime(df["date"],dayfirst=True) #converts each value form date colouns to objects of format dd / mm / yyyy
df = df[
    df["date"].dt.date == pd.Timestamp("2025-07-21").date()
] #filters to keep only required date

prices = deque(maxlen=window_size)
velocity_detector = Velocity()
acceleration_detector = Accelearation()
linreg = Regression()
event = EventDetector(trigger=3) 


fig, ax = plt.subplots(figsize=(14,6))

line, = ax.plot([], [], linewidth=2)

ax.set_title("Test Live Market")
ax.set_xlabel("Ticks")
ax.set_ylabel("Price")
ax.grid(True)

c = 0
n = 0
m = 0

vvals = []

alert_x = []
alert_y = []

accel_x = []
accel_y = []

reg_x = []
reg_y = []

notify_x = []
notify_y = []

tick = 0
for _, row in df.iterrows():
    price = row["close"]
    tick += 1

    prices.append(price)

    velocity = velocity_detector.calc(prices)
    acceleration = acceleration_detector.calc(velocity)
    gradient = linreg.calc(prices)

    if velocity is not None:
        vvals.append(velocity)


    line.set_xdata(range(len(prices)))
    line.set_ydata(prices)
    ax.scatter(alert_x, alert_y, color="red", s=50)
    ax.scatter(accel_x, accel_y,color="green", s=50)
    ax.scatter(reg_x,reg_y,color="yellow",s = 50)

    ax.relim()
    ax.autoscale_view()

    score = abs(velocity or 0) + abs(acceleration or 0) + abs(gradient or 0)
    
    notify = event.update(score)
    if notify:
        print(score, tick)
        notify_x.append(len(prices)-1)
        notify_y.append(price)
        c+=1

        
    



print(c)
vvals = sorted(vvals)

line.set_xdata(range(len(prices)))
line.set_ydata(prices)

# ax.scatter(alert_x, alert_y, color="red", s=200)
ax.scatter(notify_x,notify_y,color = "green", s = 200)
ax.relim()
ax.autoscale_view()

plt.show()