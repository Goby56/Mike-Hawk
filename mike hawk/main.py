import pygame
from config import *

class Main:
    def __init__(self):
        self._display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.disrect = self.display.get_rect()
        self.canvas = pygame.Surface(self.disrect)

    def main_loop(self):
        pass

    def events(self):
        pass

#inputs(event, hold=True, trigger=4) -> bool

class Phase:
    pass