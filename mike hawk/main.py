import pygame, time
from listener import Listener
from res.config import *
#from phases.menu import Menu
from res.widgets import MenuButton

pygame.font.init()      

class Main:
    def __init__(self):
        self._display = pygame.display.set_mode(SCREENSIZE)
        self._clock = pygame.time.Clock()
        self._previous_time = time.time()
        self.dt = 0
        self.canvas = pygame.Surface(SCREENSIZE)
        self.listener = Listener()
        #Phase.phase_stack.append(Menu(self.canvas, self.listener, self.dt))
        self.m = MenuButton(self.canvas, (100, 100), "Quit", command=quit)
        self.yeet = MenuButton(self.canvas, (300, 100), "Casper", command=lambda: print("yeet"))
        self.c = 0

    def main_loop(self):
        self.c += 0.01
        self.canvas.fill(colors["black magic"])
        self.listener.listen()
        
        self.m.update(self.listener)
        self.yeet.update(self.listener)
        self.canvas.blit(pygame.transform.scale(frames[int(self.c%8)], (100, 100)), (300, 300))
        #Phase.phase_stack[-1].update()
        #Phase.phase_stack[-1].render()

        self.listener.on_event("quit", quit)
        self.listener.on_key("escape", quit)    

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