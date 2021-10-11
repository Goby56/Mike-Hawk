import pygame
from res.config import *

class Listener:
    def __init__(self):
        self._keys = []
        self._events = []

    def listen(self):
        self._keys = []
        self._events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._events.append("quit")
            if event.type == pygame.KEYDOWN:
                self._keys.append(pygame.key.name(event.key))

    def key_pressed(self, key, hold=False, trigger=0): # if statement
        if key in self._keys and not hold:
            return True

        return False

    def on_event(self, event, func): # call function
        if event in self._events:
            func()
            

class Main:
    def __init__(self):
        self._display = pygame.display.set_mode(SCREENSIZE)
        self._clock = pygame.time.Clock()

        self.disrect = self._display.get_rect()
        self.canvas = pygame.Surface(SCREENSIZE)
        self.listener = Listener()

    def main_loop(self):
        self.listener.listen()
        self.listener.on_event("quit", lambda: quit())
        if self.listener.key_pressed("g"): print("ggaboung")

        pygame.display.update()
        self._clock.tick(60)

class Phase:
    pass

main = Main()
while True:
    main.main_loop()