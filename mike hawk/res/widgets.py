import pygame
from .config import menubutton, colors

class MenuButton:
    def __init__(self, surface, pos, text, command=None):
        self._surface = surface
        self._image = menubutton.copy()
        self._command = command
        self._text = text

        font = pygame.font.SysFont("Ariel", 20)
        font_surf = font.render(self._text, False, colors["white knight"])
        img_center, font_center = self._image.get_rect().center, font_surf.get_rect().center
        center = (img_center[0] - font_center[0], img_center[1] - font_center[1])

        self._image.blit(font_surf, center)
        self.rect = pygame.Rect(pos, self._image.get_size())

    def update(self, listener):
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            surf = pygame.transform.scale(self._image, 
                    (int(self.rect.width*1.2), int(self.rect.height*1.2)))
            listener.on_click(1, self._command)
        else: 
            surf = self._image

        rect = surf.get_rect()
        topleft = (self.rect.left - (rect.width-self.rect.width)//2, 
                self.rect.top - (rect.height - self.rect.height)//2)

        self._surface.blit(surf, topleft)

if __name__ == "__main__":
    pygame.font.init()