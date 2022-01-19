import pygame, time
from listener import Listener
from res.config import *
from res.animator import Animator
from res.timers import Timer
from phases.phase import Phase
from phases.menu import MainMenu, GameMenu
from phases.game.game import Game

pygame.font.init()

class Main: #Mike Hawk's Jungle adventure
    def __init__(self):
        self._display = pygame.display.set_mode(SCREENSIZE) #pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()
        self._previous_time = time.time()
        self.dt = 0
        self.canvas = pygame.Surface(SCREENSIZE)
        self.listener = Listener()
        MainMenu(self.canvas, self.listener).enter_phase()

    def main_loop(self):
        self.canvas.fill(colors["white knight"])
        self.listener.listen()

        self.listener.on_event("quit", quit)

        self.get_dt()
        for timer in Timer.timers:
            timer.increment(self.dt)
            
        for instance in Animator.instances:
            instance.increment(self.dt)
        
        current_phase = Phase.get_current()
        current_phase.update(self.dt)
        current_phase.render()

        if isinstance(current_phase, Game):
            self.listener.on_key("escape", lambda: GameMenu(self.canvas, self.listener, current_phase.canvas.copy()).enter_phase())

        self._display.blit(self.canvas, (0, 0))
        pygame.display.update()
        self._clock.tick(fps)

    def get_dt(self):
        current_time = time.time()
        self.dt = current_time - self._previous_time
        self._previous_time = current_time


if __name__ == "__main__":
    main = Main()
    while True:
        main.main_loop()