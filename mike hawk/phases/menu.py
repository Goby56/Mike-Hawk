import pygame, sys
sys.path.append("..")

from .phase import Phase
from .game import Game
from res.widgets import MenuButton
from res.config import dynamite_frames

class MainMenu(Phase):
    def __init__(self, canvas, listener, dt):
        self.canvas, self.listener, self.dt = canvas, listener, dt

        self.playerbutton = MenuButton(canvas, (100, 100), "New Phase", 
            command=lambda: Game(canvas, listener, dt).enter_phase())
        
        self.quitbutton = MenuButton(canvas, (100, 300), "Quit", command=quit)
        self.counter = 0

    def render(self, canvas):
        self.counter += 0.25
        self.playerbutton.update(self.listener)
        self.quitbutton.update(self.listener)
        canvas.blit(pygame.transform.scale(dynamite_frames[int(self.counter%4)], (100, 100)), (300, 300))

        