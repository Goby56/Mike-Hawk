import pygame

from phase import Phase

class Game(Phase):
    def __init__(self, canvas, listener, dt):
        self.canvas = canvas
        self.listener = listener
        self.dt = dt

    def update():
        pass

    def render():
        pass

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()