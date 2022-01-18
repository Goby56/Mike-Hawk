import pygame, sys
sys.path.append("..")

from phases.phase import Phase
from phases.game.game import Game
from res.widgets import MenuButton, MenuButtonPanel, BackgroundParalax, blurSurf
from res.config import dynamite_frames, SCREEN_RECT, SCREENSIZE, paralax_layers

class MainMenu(Phase):
    def __init__(self, canvas, listener):
        self.canvas, self.listener = canvas, listener
        self.paralax = BackgroundParalax(self.canvas, paralax_layers)

        self.buttonpanel = MenuButtonPanel(canvas, listener, (SCREENSIZE[0]/2-(MenuButton.rect.width*2), SCREENSIZE[1]/4), 3, 100, ["New Phase", "Options", "Quit"],
            [lambda: MapMenu(canvas, listener).enter_phase(), lambda: OptionsMenu(canvas, listener).enter_phase(), quit])

        self.counter = 0

    def update(self, *args, **kwargs):
        self.counter += 0.25
        self.scroll = 5
        self.paralax.update(self.scroll)
        self.paralax.render(self.canvas)
        
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
        jungle = lambda: Game(canvas, listener, "jungle").enter_phase()
        self.buttonpanel = MenuButtonPanel(canvas, listener, (SCREEN_RECT.width/2-MenuButton.rect.width*2, SCREEN_RECT.height/4), 6, 100, 
            ["Gober", "Minecraft", "Minecraft2", "Jungle", "Map 4", "Back"],
            [gober, minecraft, minecraft2, jungle, lambda: print("Map 4"), self.exit_phase]
        )

    def update(self, *args, **kwargs):
        self.buttonpanel.update()

class GameMenu(Phase):
    def __init__(self, canvas, listener, game_canvas):
        self.canvas, self.listener = canvas, listener
        self.game_canvas = blurSurf(game_canvas, 10)
        self.buttonpanel = MenuButtonPanel(self.canvas, listener, (SCREEN_RECT.width/2-MenuButton.rect.width*2, SCREEN_RECT.height/4), 3, 100, 
            ["Return", "Options", "Main Menu"], [self.exit_phase, lambda: OptionsMenu(self.canvas, listener).enter_phase(), lambda: self.exit_phase(amount=2)])

    def update(self, *args, **kwargs):
        self.canvas.blit(self.game_canvas, (0,0))
        self.buttonpanel.update()



class OptionsMenu(Phase):
    def __init__(self, canvas, listener):
        self.canvas, self.listener = canvas, listener

        self.backbutton = MenuButton(canvas, listener, (SCREEN_RECT.width/2-MenuButton.rect.width*2, SCREEN_RECT.height/4), "Back", command=self.exit_phase)

    def update(self, *args, **kwargs):
        self.backbutton.update()

        