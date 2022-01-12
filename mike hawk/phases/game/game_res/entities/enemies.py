import pygame

TILES_SIZE = 40 # import later

class Enemy:
    """
    An enemy class made for inheritance
    """
    def __init__(self, pos):
        
        # essential variables
        self.pos = list(pos)
        self.on_ground = True
        self.jumping = False

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
        value = player_pos - self.pos # may need to change order
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
        self.pos[0] += self.speed*self.direction
        # if collision
        if self.on_ground and not self.jumping:
            self.jump()

    def jump(self):
        """jumps"""


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