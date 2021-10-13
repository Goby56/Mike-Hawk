import pygame, sys
sys.path.append("..")

from .phase import Phase
from .game import Game
from res.widgets import MenuButton
from res.config import dynamite_frames

class MainMenu(Phase):
    def __init__(self, canvas, listener):
        self.canvas, self.listener = canvas, listener

        self.playerbutton = MenuButton(canvas, listener, (100, 100), "New Phase", 
            command=lambda: Game(canvas, listener).enter_phase())
        
        self.quitbutton = MenuButton(canvas, listener, (100, 300), "Quit", command=quit)
        self.counter = 0

    def update(self, dt):
        self.counter += 0.25
        self.playerbutton.update()
        self.quitbutton.update()

    def render(self):
        self.canvas.blit(pygame.transform.scale(dynamite_frames[int(self.counter%4)], (100, 100)), (300, 300))


class OptionsMenu(Phase):
    def __init__(self, canvas, listener):
        self.canvas, self.listener = canvas, listener

        #self.backbutton = MenuButton(canvas, ())

        