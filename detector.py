#Om Namo Venketesaya

class Velocity:
    def __init__(self,window = 20):
        self.window = window

    def calc(self,prices):
        if len(prices) <= self.window:
            return None
        
        curr_price = prices[-1]
        old_price = prices[-1-self.window]

        velocity = (curr_price- old_price) / self.window

        return velocity
    