import pygame, time
from listener import Listener
from res.config import *
from phases.phase import Phase
from phases.menu import Menu

pygame.font.init()      

class Main:
    def __init__(self):
        self._display = pygame.display.set_mode(SCREENSIZE)
        self._clock = pygame.time.Clock()
        self._previous_time = time.time()
        self.dt = 0
        self.canvas = pygame.Surface(SCREENSIZE)
        self.listener = Listener()
        Phase.phase_stack.append(Menu(self.canvas, self.listener, self.dt))

    def main_loop(self):
        self.canvas.fill(colors["black magic"])
        self.listener.listen()
        
        Phase.phase_stack[-1].update()
        Phase.phase_stack[-1].render()

        self.listener.on_event("quit", quit)
        self.listener.on_key("escape", quit)    

        self._display.blit(self.canvas, (0, 0))
        pygame.display.update()
        self._clock.tick(60)

    def get_dt(self):
        current_time = time.time()
        self.dt = current_time - self._previous_time
        self._previous_time = current_time


if __name__ == "__main__":
    main = Main()
    while True:
        main.main_loop()