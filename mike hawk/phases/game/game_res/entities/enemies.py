import pygame, sys
sys.path.append("..")

from res.config import game_vars
from phases.game.game_res.map import Tile

TILES_SIZE = game_vars["tile_size"]

class Enemy(pygame.sprite.Sprite):
    """
    An enemy class made for inheritance
    """
    def __init__(self, pos):
        super().__init__()

        # essential variables
        self.rect = pygame.Rect(pos, 1.5*TILES_SIZE, 3*TILES_SIZE)
        self.on_ground = True
        self.jumping = False
        self.velocity = [0, 0]

        # general stats
        self.agro_distance = 20 # tiles
        self.attack_range = 2 # tiles
        self.health = 100
        self.damage = 10
        self.crit_bonus = 1.2 # 20% of damage

        # movement
        self.speed = 5
        self.jump_height = 2 # tiles
        self.jump_force = 10

    @property
    def engaged(self) -> bool: # cannot be called before self.distance iss used
        state = True if self.distance <= self.agro_distance else False
        return state

    def get_distance(self, player_pos):
        """returns distance to players in tiles"""
        value = player_pos - self.rect.midbottom # may need to change order
        return abs(value), value/abs(value)

    def update(self, player_pos):
        """
        player_pos: player position
        """
        self.player_pos = player_pos
        self.distance, self.direction = self.get_distance(self.player_pos) # distance to player
        if self.engaged and self.distance >= self.attack_range:
            self.move()

    def move(self):
        """moves towards player"""
        self.velocity[0] = self.speed
        if self.x_collisions() and self.on_ground and not self.jumping:
            self.jump()
        self.rect.x += self.speed*self.direction

    def jump(self):
        """jumps"""
        print("jump")

    def x_collisions(self) -> bool:
        collisions = pygame.sprite.collide(self, Tile.tiles)
        for tile in collisions:
            if self.direction > 0:
                self.rect.right = tile.rect.left
            elif self.direction < 0:
                self.rect.left = tile.rect.right
            self.velocity[0] = 0
        if len(collisions): return True
        return False

    def hurt(self, amount) -> bool:
        """
        should be called when player attacks
        returns True if killed, else False
        """
        self.health -= amount
        if self.health <= 0:
            self.kill()
            return True
        return False

    def kill(self):
        """called when killed. May drop things"""


class RangedEnemy(Enemy):
    def __init__(self, pos):
        super().__init__(pos)


class SuicideBomber(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.attack_range = 1
        self.damage = 10000

    def attack(self):
        self.kill()

    def update(self, player_pos):
        super().update(player_pos)
