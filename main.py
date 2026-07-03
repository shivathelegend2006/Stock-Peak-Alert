#Om Namo Venketesaya

import time
from collections import deque #dequeu is higlhy optimised for speed
import matplotlib.pyplot as plt

from Market import testMarket
from detector import Velocity

window_size = 300 #5minutiions

market = testMarket()
prices = deque(maxlen=window_size)
velocity_detector = Velocity()

plt.ion()

fig, ax = plt.subplots(figsize=(14,6))

line, = ax.plot([], [], linewidth=2)

ax.set_title("Test Live Market")
ax.set_xlabel("Ticks")
ax.set_ylabel("Price")
ax.grid(True)

n = 0
c = 0
while n < 300:
    price = market.next_pirce()
    prices.append(price)

    velocity = velocity_detector.calc(prices)
    line.set_xdata(range(len(prices)))
    line.set_ydata(prices)

    ax.relim()
    ax.autoscale_view()

    plt.draw()
    plt.pause(0.01)

    if velocity is not None and (velocity < - 0.9 or velocity > 0.9):
        print(f"Tick: {market.tick:3d} | Price: {price:7.2f} | Velocity: {velocity:6.2f}")
        c += 1
    n += 1
    time.sleep(0.025)

print(c)
