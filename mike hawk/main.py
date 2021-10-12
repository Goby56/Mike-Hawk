import pygame
from res.config import *

class Listener:
    def __init__(self):
        self._keys = []
        self._events = []
        self._counter1 = 0
        self._counter2 = 0

    def listen(self):
        self._keys = []
        self._events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._events.append("quit")
            if event.type == pygame.KEYDOWN:
                self._keys.append(pygame.key.name(event.key))

    def key_hold(self, key, duration): # if key is hold for duration
        self._counter2 += 1

    def key_pressed(self, key, hold=False, trigger=0): # if statement
        if not hold:
            if key in self._keys:
                return True
            return False
        
        self._counter += 1
        keys = pygame.key.get_pressed()
        if key in PYGAME_CAPS_KEYS.keys():
            if keys[PYGAME_CAPS_KEYS[key]] and self._counter > trigger:
                self._counter = 0 
                return True
            return False

        if keys[eval(f"pygame.K_{key}")] and self._counter > trigger:
            self._counter = 0
            return True
        return False

    def on_event(self, event, func): # call function
        if event in self._events:
            func()
            

class Main:
    def __init__(self):
        self._display = pygame.display.set_mode(SCREENSIZE)
        self._clock = pygame.time.Clock()

        self.canvas = pygame.Surface(SCREENSIZE)
        self.listener = Listener()

    def main_loop(self):
        self.listener.listen()

        self.listener.on_event("quit", quit)

        if self.listener.key_pressed("space", hold=True, trigger=10):
            print("ggaboung")

        pygame.display.update()
        self._clock.tick(60)

class Phase:
    pass

main = Main()
while True:
    main.main_loop()