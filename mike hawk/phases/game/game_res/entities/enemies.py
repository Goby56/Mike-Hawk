import pygame, sys
sys.path.append("..")

from res.config import game_vars, colors, MAX_Y
from phases.game.game_res.map import Tile

TILES_SIZE = game_vars["tile_size"]

class Enemy(pygame.sprite.Sprite):
    """
    An enemy class made for inheritance
    """
    def __init__(self, pos):
        super().__init__()

        x, y = pos
        pos = (x*TILES_SIZE, (MAX_Y - y)*TILES_SIZE)

        # essential variables
        self.rect = pygame.Rect(pos, (1.5*TILES_SIZE, 3*TILES_SIZE))
        self.image = pygame.Surface((1.5*TILES_SIZE, 3*TILES_SIZE))
        self.image.fill(colors["red"])
        self.on_ground = True
        self.jumping = False
        self.velocity = [0, 0]
        self.scroll = pygame.Vector2(0, 0)
        self.sleeping = False

        # general stats
        self.agro_distance = 7 # tiles
        self.attack_range = 2 # tiles
        self.health = 100
        self.damage = 10
        self.crit_bonus = 1.2 # 20% of damage

        # movement
        self.speed = 3
        self.jump_height = 2 # tiles
        self.jump_force = 10

    @property
    def engaged(self) -> bool: # cannot be called before self.distance iss used
        state = True if self.distance <= self.agro_distance else False
        return state

    @property
    def collisions(self):
        return pygame.sprite.spritecollide(self, Tile.tiles, False)

    def get_distance(self, player_pos):
        """
        returns distance to players and the direction to the playes (in tiles) # fix so its acctualy in tiles
        """
        x, y = player_pos
        dx = x - self.rect.centerx
        distance = (abs(dx)**2 + abs(y - self.rect.bottom)**2)**0.5
        distance_tiles = distance // TILES_SIZE
        direction = dx/abs(dx) if dx != 0 else 0
        return distance_tiles, direction

    def update(self, player_pos, scroll):
        """
        player_pos: player position
        """
        x, y = player_pos
        self.player_pos = player_pos
        self.scroll = scroll
        self.distance, self.direction = self.get_distance(self.player_pos) # distance to player
        self.velocity[1] = game_vars["gravity"]

        if self.engaged and self.distance >= self.attack_range and not self.sleeping:
            self.move()
        
        self.on_ground = False
        self.y_collisions()
        self.rect.y += self.velocity[1]

        self.rect.x -= self.scroll.x
        self.rect.y -= self.scroll.y

    def move(self):
        """moves towards player"""
        self.velocity[0] = self.speed
        if self.x_collisions() and self.on_ground and not self.jumping:
            self.jump()

        self.rect.x += self.velocity[0]*self.direction

    def jump(self):
        """jumps"""

    def x_collisions(self):
        for tile in self.collisions:
            if self.direction > 0:
                self.rect.right = tile.rect.left
            elif self.direction < 0:
                self.rect.left = tile.rect.right
            self.velocity[0] = 0

        if len(self.collisions): return True
        return False

    def y_collisions(self):
        for tile in self.collisions:
            if self.velocity[1] < 0:
                self.rect.top = tile.rect.bottom
            elif self.velocity[1] > 0:
                self.rect.bottom = tile.rect.top
                self.on_ground = True
            self.velocity[1] = 0


    def sleep(self):
        """
        called when hit by bullet
        """
        self.sleeping = True

    def knockback(self):
        """
        called when hit with knockback attack
        """
        self.velocity[0] += self.direction*3
        self.velocity[1] -= 2
        # ändra bild

    def anger(self): # stå på bakbenen och slå på bröstet (står stilla så man hinner fly och hämta mer ammo)
        """
        called when hit with stun attack
        """
        

