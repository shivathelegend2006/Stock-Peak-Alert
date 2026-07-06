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
        
        
