import pygame, time
from res.config import *
#from phases.menu import Menu
from res.widgets import MenuButton

pygame.font.init()

class Listener:
    def __init__(self):
        self._keys = []
        self._events = []
        self._mouse = []
        self._counter1, self._counter2, self._counter3, self._counter4 = 0, 0, 0, 0 # possible error, counters may not be able to work with multible key_pressed
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

    def key_hold(self, key: str, duration: int): # if key is hold for duration, func will return % or equivilent of hold done
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

    def key_pressed(self, key: str, hold=False, trigger=0): # if statement
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

    def mouse_clicked(self, mouse: int, hold=False, trigger=0):
        if not hold:
            if mouse in self._mouse:
                return True
            return False
        
        self._counter3 += 1
        if pygame.mouse.get_pressed()[mouse-1] and self._counter3 > trigger:
            self._counter3 = 0
            return True

    def mouse_hold(self, mouse: int, duration: int):
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
            

class Main:
    def __init__(self):
        self._display = pygame.display.set_mode(SCREENSIZE)
        self._clock = pygame.time.Clock()
        self._previous_time = time.time()
        self.dt = 0
        self.canvas = pygame.Surface(SCREENSIZE)
        self.listener = Listener()
        #Phase.phase_stack.append(Menu(self.canvas, self.listener, self.dt))
        self.m = MenuButton(self.canvas, (100, 100), "test")

    def main_loop(self):
        self.canvas.fill(colors["black magic"])
        self.listener.listen()
        
        #Phase.phase_stack[-1].update()
        self.m.update()

        self.listener.on_event("quit", quit)

        if self.listener.key_pressed("space", hold=True, trigger=50):
            print("ggaboung")

        if self.listener.key_hold("w", 100) == 100:
            print("ni hao")

        if self.listener.mouse_clicked(1, hold=True):
            print("clcl")

        self._display.blit(self.canvas, (0, 0))
        pygame.display.update()
        self._clock.tick(60)

    def get_dt(self):
        current_time = time.time()
        self.dt = current_time - self._previous_time
        self._previous_time = current_time


class Phase:
    phase_stack = []

    def enter_phase(self): # Enters a new phase
        Phase.phase_stack.append(self)

    def exit_phase(self): # Exits to the previous state
        Phase.phase_stack.pop()

main = Main()
while True:
    main.main_loop()