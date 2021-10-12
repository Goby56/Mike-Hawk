import pygame, time
from res.config import *

class Listener:
    def __init__(self):
        self._keys = []
        self._events = []
        self._counter1 = 0
        self._counter2 = 0
        self._last_key = None 

    def listen(self):
        self._keys = []
        self._events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._events.append("quit")
            if event.type == pygame.KEYDOWN:
                self._keys.append(pygame.key.name(event.key))

    def key_hold(self, key, duration): # if key is hold for duration, func will return % or equivilent of hold done
        current_key = self.key_pressed(key, hold=True)
        if current_key and self._last_key:
            self._counter2 += 1
        else:
            self._counter2 = 0
        self._last_key = current_key
        if self._counter2 == duration:
            self._counter2 = 0
            return duration
        return self._counter2

    def key_pressed(self, key, hold=False, trigger=0): # if statement
        if not hold:
            if key in self._keys:
                return True
            return False
        
        self._counter1 += 1
        keys = pygame.key.get_pressed()
        if key in PYGAME_CAPS_KEYS.keys():
            if keys[PYGAME_CAPS_KEYS[key]] and self._counter1 > trigger:
                self._counter1 = 0 
                return True
            return False

        if keys[eval(f"pygame.K_{key}")] and self._counter1 > trigger:
            self._counter1  = 0
            return True
        return False

    def on_event(self, event, func): # call function
        if event in self._events:
            func()
            

class Main:
    def __init__(self):
        self._display = pygame.display.set_mode(SCREENSIZE)
        self._clock = pygame.time.Clock()
        self._previous_time = time.set()
        self.dt = 0

        self.canvas = pygame.Surface(SCREENSIZE)
        self.listener = Listener()

    def main_loop(self):
        self.listener.listen()

        self.listener.on_event("quit", quit)

        if self.listener.key_pressed("space", hold=True, trigger=50):
            print("ggaboung")

        if self.listener.key_hold("w", 100) == 100:
            print("ni hao")

        pygame.display.update()
        self._clock.tick(60)

    def get_dt(self):
        current_time = time.time()
        self.dt = current_time - self._previous_time
        self._previous_time = current_time

class Phase:
    pass

main = Main()
while True:
    main.main_loop()