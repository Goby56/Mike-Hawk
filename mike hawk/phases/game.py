import pygame, sys
sys.path.append("..")

from .phase import Phase
from res.widgets import MenuButton

# temp import
import json, os
from res.config import tile_frames, sprite_dir, dev_level, game_vars


class Game(Phase):
    def __init__(self, canvas, listener):
        self.canvas = canvas
        self.listener = listener
        
        self.backbutton = MenuButton(canvas, listener, (100, 150), "Pop Phase",
            command=self.exit_phase)
        self.tiles = pygame.sprite.Group()
        self.tile_size = 40

        self.level = dev_level
        self.map = self.crop_map(self.level["map"])
        self.place_tiles(self.tile_size)

        player_dim = (int(self.tile_size*1.5), int(self.tile_size*3))
        spawn = (self.level["spawn"][0]*self.tile_size - player_dim[0]//2, self.canvas.get_height() - self.level["spawn"][1]*self.tile_size + player_dim[1])
        self.player = Player(listener, canvas, spawn, player_dim)
        self.camera = Camera(self.player, canvas)

        self.scroll = pygame.Vector2(0, 0)

        

    def update(self, dt):
        self.get_scroll(350, 350)

        self.player.update(dt, self.tiles, self.scroll)
        self.limit_player()

        self.tiles.update(self.scroll)
        self.backbutton.update()

    def render(self):
        self.tiles.draw(self.canvas)
        self.player.render()

    def crop_map(self, map):
        for i, row in enumerate(map):
            if any(row): break
        lengths = []
        for j, tile in enumerate(map[i:][::-1]):
            if tile: lengths.append(j)
        return [row[min(lengths):] for row in map[i:]]
        
    def place_tiles(self, size):
        for r, row in enumerate(self.map):
            for c, tile in enumerate(row):
                if tile: self.tiles.add(Tile((c,r), size, tile_frames[tile-1]))

    def get_world_dimensions(self):
        return (len(self.map[0]) * self.tile_size, len(self.map) * self.tile_size)

    def limit_player(self):
        if self.player.pos.x > self.canvas.get_width() - self.player.width:
            self.player.pos.x = self.canvas.get_width() - self.player.width
        if self.player.pos.x < 0:
            self.player.pos.x = 0

    def get_scroll(self, x_offset, y_offset):
        if self.player.abs_x < x_offset - self.player.width/2:
            self.scroll.x = 0
            return
        elif self.player.abs_x > self.get_world_dimensions()[0] - x_offset - self.player.width/2:
            self.scroll.x = 0
            return
            
        right_bound, left_bound = self.canvas.get_width() - x_offset, x_offset
        if not left_bound < self.player.rect.centerx < right_bound:
            self.scroll.x = self.player.velocity.x
        else:
            self.scroll.x = 0


class Camera: # dont remove, want to improve
    def __init__(self, player, canvas):
        self.player = player
        self.offset = pygame.Vector2(0,0)
        self.CANVAS_W, self.CANVAS_H = canvas.get_size()

        # Offset for follow method
        self.MIDDLE = pygame.Vector2(-self.CANVAS_W/2, -self.CANVAS_H/2 + player.rect.y/2 - 100)
        self.method = "follow"

    def get_offset(self):
        exec(f"self.{self.method}()")
        return self.offset

    def follow(self):
        self.offset.x += self.player.rect.x + self.MIDDLE.x
        self.offset.y += self.player.rect.y + self.MIDDLE.y

    def border(self):
        pass

    def auto(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, listener, canvas, pos, size):
        super().__init__()
        self.listener = listener
        self.canvas = canvas
        self.pos = pygame.Vector2(pos)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(sprite_dir,
             "mike.png")), (size))
        self.width, self.height = self.image.get_width(), self.image.get_height()
        self.rect = self.image.get_rect(midbottom=self.pos)
        self.collisions = {"right":False, "left":False, "top":False, "bottom":False}
        self.acceleration = pygame.Vector2(0, game_vars["gravity"])
        self.velocity = pygame.Vector2(0, 0)
        self.onground = False
        self.total_scroll = pygame.Vector2(0, 0)

    @property
    def abs_x(self):
        return self.pos.x - self.total_scroll.x

    @property
    def abs_y(self):
        return self.pos.y - self.total_scroll.y

    def update(self, dt, collisions_objects, scroll):
        self.total_scroll.xy -= scroll.xy
        self.pos.xy -= scroll.xy

        self.horizontal_movement(dt)
        self.handle_collisions(self.get_collisions(collisions_objects), axis=0)
        self.vertical_movement(dt)
        self.handle_collisions(self.get_collisions(collisions_objects), axis=1)
        
    def render(self):
        self.canvas.blit(self.image, self.pos.xy)

    def horizontal_movement(self, dt):
        dt *= 60
        key_a = self.listener.key_pressed("a", hold=True)
        key_d = self.listener.key_pressed("d", hold=True)
        direction = key_d - key_a
        self.acceleration.x = game_vars["speed"]*direction

        self.velocity.x += dt*(self.acceleration.x + self.velocity.x*game_vars["friction"])
        self.limit_velocity(game_vars["max_vel"])
        self.pos.x += self.velocity.x*dt + 0.5*(self.acceleration.x * dt**2)

        self.rect.x = self.pos.x

    def vertical_movement(self, dt):
        dt *= 60
        if self.listener.key_pressed("space", hold=True) and self.onground: # set onground to False
            self.velocity.y = -game_vars["jump strength"]
        self.onground = False

        self.velocity.y += self.acceleration.y*dt
        self.pos.y += self.velocity.y*dt + 0.5*(self.acceleration.y * dt**2)
        
        self.rect.y = self.pos.y

    def limit_velocity(self, max_velocity):
        if abs(self.velocity.x) > max_velocity:
            self.velocity.x = max_velocity if self.velocity.x > 0 else -max_velocity 
        if abs(self.velocity.x) < 0.1: self.velocity.x = 0

    def handle_collisions(self, tile_collisions, axis):
        if tile_collisions:
            for tile in tile_collisions:
                if axis == 0:
                    if self.velocity.x > 0: 
                        self.rect.right = tile.rect.left
                        self.velocity.x = 0
                    elif self.velocity.x < 0: 
                        self.rect.left = tile.rect.right
                        self.velocity.x = 0
                elif axis == 1:
                    if self.velocity.y > 0:
                        self.rect.bottom = tile.rect.top
                        self.velocity.y = 0
                        self.onground = True
                    elif self.velocity.y < 0: 
                        self.rect.top = tile.rect.bottom
                        self.velocity.y = 0
            self.pos.xy = self.rect.topleft

    def get_collisions(self, group):
        collisions = pygame.sprite.spritecollide(self, group, False)
        return collisions


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size, image):
        super().__init__()
        self.size = size, size
        self.pos = pygame.Vector2(pos[0]*self.size[0], pos[1]*self.size[1])
        self.image = image
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(topleft = self.pos)
        self.total_scroll = pygame.Vector2(0, 0)

    @property
    def abs_x(self):
        return self.pos.x - self.total_scroll.x

    @property
    def abs_y(self):
        return self.pos.y - self.total_scroll.y

    def update(self, scroll):
        self.total_scroll.xy -= scroll.xy
        self.pos.xy -= scroll.xy
        self.rect.topleft = self.pos.xy

