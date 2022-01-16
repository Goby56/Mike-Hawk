import pygame, sys
sys.path.append("..")

from phases.phase import Phase
from phases.game.game import Game
from res.widgets import MenuButton, MenuButtonPanel
from res.config import dynamite_frames, SCREEN_RECT

class MainMenu(Phase):
    def __init__(self, canvas, listener):
        self.canvas, self.listener = canvas, listener

        self.buttonpanel = MenuButtonPanel(canvas, listener, (200, 100), 3, 20, ["New Phase", "Options", "Quit"],
            [lambda: MapMenu(canvas, listener).enter_phase(), lambda: OptionsMenu(canvas, listener).enter_phase(), quit])

        self.counter = 0

    def update(self, *args, **kwargs):
        self.counter += 0.25
        self.buttonpanel.update()

    def render(self):
        scaled_surface = pygame.transform.scale(dynamite_frames[int(self.counter%4)], (100, 100))
        rotated_surface = pygame.transform.rotate(scaled_surface, self.counter*4)
        frame_rect =rotated_surface.get_rect()
        padding = 10
        self.canvas.blit(rotated_surface, (SCREEN_RECT.width-frame_rect.width-padding, SCREEN_RECT.height-frame_rect.height-padding))


class MapMenu(Phase):
    def __init__(self, canvas, listener):
        gober = lambda: Game(canvas, listener, "gober").enter_phase()
        minecraft = lambda: Game(canvas, listener, "minecraft").enter_phase()
        minecraft2 = lambda: Game(canvas, listener, "minecraft2").enter_phase()
        self.buttonpanel = MenuButtonPanel(canvas, listener, (200, 100), 6, 20, 
            ["gober", "minecraft", "minecraft2", "Map 3", "Map 4", "Back"],
            [gober, minecraft, minecraft2, 
            lambda: print("Map 3"), lambda: print("Map 4"), self.exit_phase]
        )

    def update(self, *args, **kwargs):
        self.buttonpanel.update()


class OptionsMenu(Phase):
    def __init__(self, canvas, listener):
        self.canvas, self.listener = canvas, listener

        self.backbutton = MenuButton(canvas, listener, (100, 300), "Back", command=self.exit_phase)

    def update(self, *args, **kwargs):
        self.backbutton.update()

        