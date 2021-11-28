#import sys, time
from .config import fps

class Timer:
    timers = []

    def __init__(self, type_: str, format_: str, count: int, on=False):
        if type_ == "up":
            self.type = 1
            self.requirement = count*60 if format_ == "minutes" else count
            self.time = 0
        elif type_ == "down":
            self.type = -1
            self.time = count*60 if format_ == "minutes" else count
            self.starting_time = count
        self.format = format_
        self.running = on
        self.timers.append(self)

    def update(self):
        if self.type == 1 and self.time >= self.requirement:
            self.time = self.requirement
            self.running = False
        if self.type == -1 and self.time <= 0:
            self.time = 0
            self.running = False
    
    def increment(self, dt):
        if self.running:
            if self.format == "ticks":
                self.time += self.type  
            else:
                self.time += dt*self.type
        self.update()
    
    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def reset(self):
        if self.type == 1:
            self.time = 0
        elif self.type == -1:
            self.time = self.starting_time
        self.running = False

    def set_time(self, time):
        self.time = time

    def get_time(self):
        return self.time

    def finished(self):
        if self.type == 1 and self.time == self.requirement:
            return True
        elif self.type == -1 and self.time == 0:
            return True
        else:
            return False

        

    
