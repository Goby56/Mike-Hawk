import pygame, sys
sys.path.append("..")

from .phase import Phase
from res.widgets import MenuButton

class Game(Phase):
    def __init__(self, canvas, listener, dt):
        self.canvas = canvas
        self.listener = listener
        self.dt = dt

        self.backbutton = MenuButton(canvas, (100, 150), "Pop Phase",
            command=lambda: [self.exit_phase(), print("back")])

    def update(self):
        self.backbutton.update(self.listener)

    def render(self):
        pass

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()