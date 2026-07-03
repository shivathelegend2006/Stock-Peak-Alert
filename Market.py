#Om Namo Venketesaya
import random
import time

class testMarket:
    def __init__(self,start = 100):
        self.price = start
        self.tick = 0

    def next_pirce(self):
        self.tick +=1

        movement = random.uniform(-0.8,0.8) #creates ranfdom number between -.9 and .8

        if 80 <= self.tick < 90:
            movement += 2.5      # Rally

        elif 170 <= self.tick < 180:
            movement -= 3         # Crash

        elif 240 <= self.tick < 250:
            movement += 2

        elif 320 <= self.tick < 330:
            movement -= 2.5

        self.price += movement

        return round(self.price, 2)
    