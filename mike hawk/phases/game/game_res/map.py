import pygame, sys, math
sys.path.append("..")

from res.config import game_vars

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size, image):
        super().__init__()
        self.size = size, size
        self.pos = pygame.Vector2(pos[0]*self.size[0], pos[1]*self.size[1])
        self.image = image
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(topleft = self.pos)
        self.scroll_offset = pygame.Vector2(0, 0)

    @property
    def abs_x(self):
        return self.pos.x + self.scroll_offset.x

    @property
    def abs_y(self):
        return self.pos.y - self.scroll_offset.y

    def update(self, scroll):
        self.scroll_offset += scroll
        self.pos.x += -(scroll.x)
        self.pos.y += -(scroll.y)

        self.rect.topleft = self.pos.xy


class Trigger(pygame.sprite.Sprite):
    def __init__(self, pos, command, type):
        super().__init__()
        self.command, self.type = command, int(type)

        size = game_vars["tile_size"]
        self.pos = pygame.Vector2(pos[0]*size, pos[1]*size)
        self.rect = pygame.Rect(self.pos.xy, (size, size))

        self.player_in_trigger = False

    def update(self, scroll):
        self.pos.x -= scroll.x
        self.pos.y -= scroll.y

        self.rect.topleft = self.pos.xy


class TriggerType:
    def __init__(self, command, type, mesh):
        self.command, self.type, self.mesh = command, type, mesh
        self.triggerd = False