import pygame
from res.config import PYGAME_CAPS_KEYS

class Listener:
    def __init__(self):
        self._keys = []
        self._events = []
        self._mouse = []
        self._counter1, self._counter2 = 0, 0
        self._counter3, self._counter4 = 0, 0
        self._last_key = None
        self._last_mouse = None

    def listen(self):
        self._keys, self._events, self._mouse = [], [], []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._events.append("quit")
            if event.type == pygame.KEYDOWN:
                self._keys.append(pygame.key.name(event.key))
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse.append(event.button)

    def key_hold(self, key: str, duration: int): # fix for multible holds
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

    def key_pressed(self, key: str, hold=False, trigger=1): # if statement
        if not hold:
            if key in self._keys:
                return True
            return False
        
        self._counter1 += 1
        keys = pygame.key.get_pressed()
        if key in PYGAME_CAPS_KEYS.keys():
            if keys[PYGAME_CAPS_KEYS[key]] and self._counter1 % trigger == 0:
                return True
            return False

        if keys[eval(f"pygame.K_{key}")] and self._counter1 % trigger == 0:
            return True
        return False

    def mouse_clicked(self, mouse: int, hold=False, trigger=1):
        if not hold:
            if mouse in self._mouse:
                return True
            return False
        
        self._counter3 += 1
        if pygame.mouse.get_pressed()[mouse-1] and self._counter3 % trigger == 0:
            self._counter3 = 0
            return True

    def mouse_hold(self, mouse: int, duration: int): # fix for multible holds
        current_mouse = self.mouse_clicked(mouse, hold=True)
        if current_mouse and self._last_mouse:
            self._counter4 += 1
        else:
            self._counter4 = 0

        if self._counter4 == duration:
            self._counter4 = 0
            return duration
        return self._counter4

    def on_key(self, key: str, func):
        if key in self._keys:
            func()

    def on_click(self, mouse: int, func):
        if mouse in self._mouse:
            func()

    def on_event(self, event, func): # call function
        if event in self._events:
            func()