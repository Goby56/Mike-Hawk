import pygame
from res.config import PYGAME_CAPS_KEYS

class Listener:
    """
    Example:\n
    listener = Listener()\n
    while True:\n
        listner.listen()\n
        listner.on_event("quit", quit)\n
        listener.key_pressed("a", hold=True, trigger=10, id="a_pressed_0") # id is counter id
    """
    def __init__(self):
        self._keys = []
        self._events = []
        self._mouse = []
        self._keys_up = []
        self._counters = {}
        self._last_key = None
        self._last_mouse = None

    def _create_key(self, id):
        if not id in self._counters.keys():
            self._counters[id] = 0

    def _holder(self, duration, id, current, last, mouse=False):
        if current and last:
            self._counters[id] += 1
        else:
            self._counters[id] = 0

        if mouse: self._last_mouse = current
        else: self._last_key = current

        if self._counters[id] >= duration:
            return duration
        return self._counters[id]

    def listen(self):
        self._keys, self._events, self._mouse = [], [], []
        self._keys_up = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._events.append("quit")
            if event.type == pygame.KEYDOWN:
                self._keys.append(pygame.key.name(event.key))
            if event.type == pygame.KEYUP:
                self._keys_up.append(pygame.key.name(event.key))
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse.append(event.button)
            

    def key_hold(self, key: str, duration: int, id: str):
        self._create_key(id)
        current_key = self.key_pressed(key, hold=True)
        return self._holder(duration, id, current_key, self._last_key)

    def key_pressed(self, key: str, hold=False, trigger=1, id=""):
        self._create_key(id)
        if not hold:
            if key in self._keys:
                return True
            return False
        
        self._counters[id] += 1
        keys = pygame.key.get_pressed()
        if key in PYGAME_CAPS_KEYS.keys():
            if keys[PYGAME_CAPS_KEYS[key]] and self._counters[id] % trigger == 0:
                return True
            return False
        if keys[eval("pygame.K_" + key)] and self._counters[id] % trigger == 0:
            return True
        return False

    def key_up(self, key):
        if key in self._keys_up:
            return True
        return False

    def mouse_clicked(self, mouse: int, hold=False, trigger=1, id=""):
        self._create_key(id)
        if not hold:
            if mouse in self._mouse:
                return True
            return False
        
        self._counters[id] += 1
        if pygame.mouse.get_pressed()[mouse-1] and self._counters[id] % trigger == 0:
            self._counters[id] = 0
            return True

    def mouse_hold(self, mouse: int, duration: int, id=""):
        self._create_key(id)
        current_mouse = self.mouse_clicked(mouse, hold=True)
        return self._holder(duration, id, current_mouse, self._last_mouse, True)

    def on_key(self, key: str, func):
        if key in self._keys:
            func()

    def on_click(self, mouse: int, func):
        if mouse in self._mouse:
            func()

    def on_event(self, event, func): # call function
        if event in self._events:
            func()