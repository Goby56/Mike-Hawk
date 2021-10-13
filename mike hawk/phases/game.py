import pygame, sys
sys.path.append("..")

from .phase import Phase
from res.widgets import MenuButton

# temp import
import json, os
from res.config import tile_frames, sprite_dir, dev_level

class Game(Phase):
    def __init__(self, canvas, listener):
        self.canvas = canvas
        self.listener = listener
        
        self.backbutton = MenuButton(canvas, listener, (100, 150), "Pop Phase",
            command=self.exit_phase)
        self.tiles = pygame.sprite.Group()
        self.place_tiles()

        self.player = Player(listener, canvas, (300,300))
        self.camera = Camera(self.player, canvas)

    def update(self, dt):
        camera_offset = self.camera.get_offset()

        player_tile_collisions = pygame.sprite.spritecollide(self.player, self.tiles, dokill=False)
        self.player.update(dt, camera_offset, player_tile_collisions)

        self.tiles.update(camera_offset)
        self.backbutton.update()

    def render(self):
        self.tiles.draw(self.canvas)
        self.player.render()

    def place_tiles(self):
        level = dev_level["map"]
        for r, row in enumerate(level):
            for c, tile in enumerate(row):
                if tile: self.tiles.add(Tile((c,r), tile_frames[tile-1]))

class Camera:
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
        self.offset.x += self.player.rect.x - self.offset.x + self.MIDDLE.x
        self.offset.y += self.player.rect.y - self.offset.y + self.MIDDLE.y

    def border(self):
        pass

    def auto(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, listener, canvas, pos):
        super().__init__()
        self.listener = listener
        self.canvas = canvas
        self.pos = pygame.Vector2(pos)
        self.image = pygame.image.load(os.path.join(sprite_dir, "mike.png"))
        self.rect = self.image.get_rect(topleft = self.pos)
        self.collisions = {"right":False, "left":False, "top":False, "bottom":False}
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 5
        self.gravity = 0.1

    def update(self, dt, camera_offset, tile_collisions):
        self.horizontal_movement(dt)
        self.handle_collisions(tile_collisions, axis=0)
        self.vertical_movement(dt)
        self.handle_collisions(tile_collisions, axis=1)
        
        self.pos.xy += -camera_offset
        self.rect.topleft = self.pos.xy

    def render(self):
        self.canvas.blit(self.image, self.pos.xy)

    def horizontal_movement(self, dt):
        if self.listener.key_pressed("a", hold=True):
            self.velocity.x = -self.speed
        if self.listener.key_pressed("d", hold=True):
            self.velocity.x = self.speed

        if self.listener.key_up("a") or self.listener.key_up("d"):
            self.velocity.x = 0

        self.pos.x += self.velocity.x
        self.rect.x = self.pos.x

    def vertical_movement(self, dt):
        self.velocity.y += self.gravity
        self.pos.y += self.velocity.y
        self.rect.y = self.pos.y

    def handle_collisions(self, collision_list, axis):
        if len(collision_list) > 0:
            if axis == 0:
                for sprite in collision_list:
                    if self.velocity.x > 0:
                        self.rect.right = sprite.rect.left
                        self.velocity.x = 0
                    elif self.velocity.x < 0:
                        self.rect.left = sprite.rect.right
                        self.velocity.x = 0
            self.pos.x = self.rect.x

            if axis == 1:
                for sprite in collision_list:
                    if self.velocity.y > 0:
                        self.rect.bottom = sprite.rect.top
                        self.velocity.y = 0
                    elif self.velocity.y < 0:
                        self.rect.top = sprite.rect.bottom
            self.pos.y = self.rect.y

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.size = (100,100)
        self.pos = pygame.Vector2(pos[0]*self.size[0], pos[1]*self.size[1])
        self.pos[0] += -600
        self.image = image
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(topleft = self.pos)

    def update(self, camera_offset):
        self.pos.xy += -camera_offset
        self.rect.topleft = self.pos.xy