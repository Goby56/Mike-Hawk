import pygame, sys
sys.path.append("..")

from res.config import gui, gui_selection

class GUI(pygame.Surface):
    def __init__(self, pos):
        size = gui.get_rect().size()
        super().__init__(size)
        self.rect = self.get_rect(center=pos)

    def set_current(self, index):
        pass

    def set_ammo(self, amount):
        pass

    def set_health(self, amount):
        pass