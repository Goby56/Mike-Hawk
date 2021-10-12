import pygame
from .config import menubutton, colors

class MenuButton:
    def __init__(self, surface, pos, text, command=None):
        self._surface, self.pos = surface, pos
        self._image = menubutton
        font = pygame.font.SysFont("Ariel", 20)
        font_surf = font.render(text, False, colors["white knight"])
        img_center, font_center = self._image.get_rect().center, font_surf.get_rect().center
        self._image.blit(font_surf, (img_center[0] - font_center[0], img_center[1] - font_center[1]))


    def update(self):
        self._surface.blit(self._image, self.pos)

if __name__ == "__main__":
    pygame.font.init()