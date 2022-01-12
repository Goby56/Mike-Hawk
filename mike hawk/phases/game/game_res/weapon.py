import pygame, sys, math
sys.path.append("..")

from phases.game.game_res.entities.bullet import Bullet
from phases.game.game import get_angle

class Weapon(pygame.sprite.Sprite):
    def __init__(self, listener, stats):
        super().__init__()
        self.listener = listener
        self.rof = stats["rof"]
        self.reload = stats["reload"]
        self.recoil = stats["recoil"]
        self.velocity = stats["velocity"]

        self.rect = pygame.Rect(0, 0, 10, 10)
        self.nozzle = self.rect.midright # change with rotation
        self.reloading = False

    def fire(self, angle, bullets):
        bullets.add(Bullet(self.nozzle, angle, self.velocity))
        # set player recoil vel

    def update(self, bullets):
        mouse = pygame.mouse.get_pos()
        angle = get_angle(self.nozzle, mouse)
        if self.listener.mouse_clicked(1, hold=True, trigger=self.rof, id="weapon_fire") and not self.reloading:
            self.fire(angle, bullets)

    def render(self):
        pass