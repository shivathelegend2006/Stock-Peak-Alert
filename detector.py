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
    def __init__(self,trigger = 3, end_after = 5):
        self.trigger = trigger
        self.end_after = end_after

        self.active = False
        self.idel_ticks = 0

    def update(self,score):
        if not self.active: #Idel
            if score >= self.trigger: #event started
                self.active = True        
                self.idel_ticks = 0

                return "START"
            
            return None
        
        if score >= self.trigger: #ongoing but start of new
            self.idel_ticks = 0
            return "ONGOING"
        
        self.idel_ticks += 1
        if self.idel_ticks >= self.end_after: #ongoing for more than 5 but not more reponse
            self.active = False
            self.idel_ticks = 0

            return "END"
        
        return "ONGOING" #siply ongoing