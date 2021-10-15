import pygame, sys
sys.path.append("..")

from .phase import Phase
from res.widgets import MenuButton

# temp import
import json, os
from res.config import tile_frames, sprite_dir, dev_level

def xcollision(rect1, rect2, temp):
    pygame.draw.rect(temp, (255, 0, 0), rect1)
    if not rect1.colliderect(rect2):
        return False
    if rect1.left < rect2.right:
        return True
    elif rect1.right > rect2.left:
        return True
    return False

def ycollision(rect1, rect2):
    if not rect1.colliderect(rect2):
        return False
    if rect1.top < rect2.bottom:
        return True
    elif rect1.bottom > rect2.top:
        return True
    return False


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

        self.player.update(dt, self.tiles, camera_offset)

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
        self.rect = self.image.get_rect(midbottom=self.pos)
        self.collisions = {"right":False, "left":False, "top":False, "bottom":False}
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 5
        self.gravity = 0.1
        self.onground = False

    def update(self, dt, collisions_objects, camera):
        self.horizontal_movement(dt)
        self.handle_collisions(self.get_collisions(collisions_objects), axis=0)
        self.vertical_movement(dt)
        self.handle_collisions(self.get_collisions(collisions_objects), axis=1)
        #self.pos.xy += -camera_offset

    def render(self):
        pygame.draw.rect(self.canvas, (255, 0, 0), self.rect)
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

    def handle_collisions(self, tile_collisions, axis):
        if tile_collisions:
            for tile in tile_collisions:
                if axis == 0:
                    if self.velocity.x > 0: self.rect.right = tile.rect.left
                    elif self.velocity.x < 0: self.rect.left = tile.rect.right
                elif axis == 1:
                    if self.velocity.y > 0:
                        self.rect.bottom = tile.rect.top
                        self.velocity.y = 0
                        self.onground = True
                    elif self.velocity.y < 0: self.rect.top = tile.rect.bottom
            self.pos.xy = self.rect.topleft

    def get_collisions(self, group):
        collisions = pygame.sprite.spritecollide(self, group, False)
        return collisions


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.size = (100,100)
        self.pos = pygame.Vector2(pos[0]*self.size[0], pos[1]*self.size[1])
        #.pos[0] += -600
        self.image = image
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(topleft = self.pos)

    def update(self, camera_offset):
        #self.pos.xy += -camera_offset
        self.rect.topleft = self.pos.xy

        # if collision_list:
            #     for tile in collision_list:
            #         if axis:
            #             if self.velocity.y > 0: self.rect.bottom = tile.rect.top
            #             elif self.velocity.y < 0: self.rect.top = tile.rect.bottom
            #             self.velocity.y = 0
            #         else:
            #             if self.velocity.x < 0 and self.rect.bottom != tile.rect.top: 
            #                 self.rect.left = tile.rect.right
            #             elif self.velocity.x > 0 and self.rect.bottom != tile.rect.top: 
            #                 self.rect.right = tile.rect.left
            #             self.velocity.x = 0
            #     self.pos.xy = self.rect.topleft
           
           
           
            # for tile in player_collisions[cset]:
            #     if cset == "x_tiles":
            #         if self.velocity.x < 0: self.rect.left = tile.right
            #         elif self.velocity.x > 0: self.rect.right = tile.left
            #         self.velocity.x = 0
            #     elif cset == "y_tiles":
            #         if self.velocity.y > 0: self.rect.bottom = tile.top
            #         elif self.velocity.y < 0: self.rect.top = tile.bottom
            #         self.velocity.y = 0
            # self.pos.xy = self.rect.topleft 
