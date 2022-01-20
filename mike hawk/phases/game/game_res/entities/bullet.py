import pygame, sys, math
sys.path.append("..")

from res.config import colors

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle: int, speed: int):
        super().__init__()
        self.angle = math.radians(angle)
        self.speed = speed
        
        temp_size = 20
        self.rect = pygame.Rect(pos, (20, 20))
        self.image = pygame.Surface((temp_size, temp_size))
        self.image.fill(colors["black"])


    def update(self, scroll, tiles):
        self.rect.x += math.cos(self.angle) * self.speed - scroll.x
        self.rect.y += math.sin(self.angle) * self.speed - scroll.y
        if pygame.sprite.spritecollide(self, tiles, dokill=False):
            self.kill()