import pygame, time
from listener import Listener
from res.config import *
from phases.phase import Phase
from phases.menu import MainMenu

pygame.font.init()

class Main:
    def __init__(self):
        self._display = pygame.display.set_mode(SCREENSIZE, pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()
        self._previous_time = time.time()
        self.dt = 0
        self.timers = {}
        self.canvas = pygame.Surface(SCREENSIZE)
        self.listener = Listener()
        MainMenu(self.canvas, self.listener).enter_phase()

    def main_loop(self):
        self.canvas.fill(colors["white knight"])
        self.listener.listen()

        self.listener.on_event("quit", quit)
        self.listener.on_key("escape", quit)

        self.get_dt()
        for timer in self.timers:
            timer += self.dt
        
        current_phase = Phase.get_current()
        current_phase.update(self.dt)
        current_phase.render()   

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