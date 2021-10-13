import pygame, sys

from pygame.transform import rotate
sys.path.append("..")

from .phase import Phase
from .game import Game
from res.widgets import MenuButton, MenuButtonPanel
from res.config import dynamite_frames

class MainMenu(Phase):
    def __init__(self, canvas, listener):
        self.canvas, self.listener = canvas, listener

        self.buttonpanel = MenuButtonPanel(canvas, listener, (200, 100), 3, 20, ["New Phase", "Options", "Quit"],
            [lambda: MapMenu(canvas, listener).enter_phase(), lambda: OptionsMenu(canvas, listener).enter_phase(), quit])

        self.counter = 0

    def update(self, dt):
        self.counter += 0.25
        self.buttonpanel.update()

    def render(self):
        scaled_surface = pygame.transform.scale(dynamite_frames[int(self.counter%4)], (100, 100))
        rotated_surface = pygame.transform.rotate(scaled_surface, self.counter*4)
        self.canvas.blit(rotated_surface, (300, 300))


class MapMenu(Phase):
    def __init__(self, canvas, listener):
        printname = lambda name: print(name)
        self.buttonpanel = MenuButtonPanel(canvas, listener, (200, 100), 6, 20, 
            ["Dev Map", "Map 1", "Map 2", "Map 3", "Map 4", "Map 5"],
            [lambda: Game(canvas, listener), lambda: print("Map 1"), lambda: print("Map 2"), 
            lambda: print("Map 3"), lambda: print("Map 4"), lambda: print("Map 5")]
        )

    def update(self, dt):
        self.buttonpanel.update()



class OptionsMenu(Phase):
    def __init__(self, canvas, listener):
        self.canvas, self.listener = canvas, listener

        self.backbutton = MenuButton(canvas, listener, (100, 300), "Back", command=self.exit_phase)

    def update(self, dt):
        self.backbutton.update()

        