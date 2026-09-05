#Om Namo Venketesaya
import numpy as np

class Velocity:
    def __init__(self,lookback = 25):
        self.window = lookback

    def calc(self,prices):
        if len(prices) <= self.window:
            return None
        
        curr_price = prices[-1]
        old_price = prices[-1-self.window]

        velocity = (curr_price- old_price) / self.window

        return velocity
    

class Accelearation:
    def __init__(self):
        self.prev_velocity  = None

    def calc(self,velocity):
        if velocity is None:
            return None
        
        if self.prev_velocity is None:
            self.prev_velocity = velocity
            return None
        
        accelearation = velocity - self.prev_velocity
        self.prev_velocity = velocity

        return accelearation


class Regression:
    def __init__(self,lookback = 20):
        self.lookback = lookback

    def calc(self,prices):

        if len(prices) < self.lookback:
            return None
        
        y = np.array(list(prices)[-self.lookback:])
        x = np.arange(self.lookback)

        m,c = np.polyfit(x,y,1)
        
        return m


class EventDetector:
    def __init__(self, trigger=0.5, notify=2.0, decay=0.85, cooldown_period=60):
        self.trigger = trigger
        self.notify = notify
        self.decay = decay
        
        self.confidence = 0
        self.cooldown_period = cooldown_period
        self.ticks_since_last_alert = 9999 

    def update(self, score):

        self.ticks_since_last_alert += 1

        if score > self.trigger:
            self.confidence += (score - self.trigger)
        else:
            self.confidence *= self.decay

        if self.confidence < 0.05:
            self.confidence = 0

        notify = False
    
        if self.confidence >= self.notify and self.ticks_since_last_alert >= self.cooldown_period:
            notify = True
            self.confidence = 0 
            self.ticks_since_last_alert = 0 

        return notify