import pygame, sys
sys.path.append("..")

from .phase import Phase
from res.widgets import MenuButton
from res.config import frames

class Menu(Phase):
    def __init__(self, canvas, listener, dt):
        self.canvas, self.listener, self.dt = canvas, listener, dt
        self.m = MenuButton(canvas, (100, 100), "Quit", command=quit)
        self.yeet = MenuButton(canvas, (300, 100), "Casper", command=lambda: print("yeet"))
        self.c = 0

    def render(self):
        self.c += 0.05
        self.m.update(self.listener)
        self.yeet.update(self.listener)
        self.canvas.blit(pygame.transform.scale(frames[int(self.c%8)], (100, 100)), (300, 300))

        