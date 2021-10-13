import pygame, sys
sys.path.append("..")

from .phase import Phase
from res.widgets import MenuButton

# temp import
import json, os
from res.config import tile_frames, _base_dir, sprite_dir

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
        self.player.update(dt)
        self.tiles.update(self.player.pos.xy)
        self.backbutton.update()

    def render(self):
        self.tiles.draw(self.canvas)
        self.player.render()

    def place_tiles(self):
        with open(os.path.join(_base_dir, "temp_world.json")) as f:
            data = json.load(f)
        for r, row in enumerate(data["map"]):
            for c, tile in enumerate(row):
                if tile == 1:
                    self.tiles.add(Tile((c,r), tile_frames[4]))

class Camera:
    def __init__(self, player, canvas):
        self.player = player
        self.offset = pygame.Vector2(0,0)
        self.CANVAS_W, self.CANVAS_H = canvas.get_size()

        # Offset for follow method
        self.MIDDLE = pygame.Vector2(-self.CANVAS_W/2 + player.rect.x/2, -self.CANVAS_H/2 + player.rect.y/2)
        self.method = "follow"

    def get_offset(self):
        exec(f"{self.method}()")

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

        self.velocity = pygame.Vector2(0, 0)
        self.speed = 5

    def update(self, dt):
        self.movement(dt)

    def render(self):
        self.canvas.blit(self.image, self.pos.xy)

    def movement(self, dt):
        if self.listener.key_pressed("a", hold=True):
            print("dpws")
            self.velocity.x = -self.speed
        if self.listener.key_pressed("d", hold=True):
            print("dpws")
            self.velocity.x = self.speed

        if self.listener.key_up("a") or self.listener.key_up("d"):
            print("up")
            self.velocity.x = 0

        self.pos.x += self.velocity.x
        self.pos.y += self.velocity.y
        

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.size = (100,100)
        self.pos = [pos[0]*self.size[0], pos[1]*self.size[1]]
        self.pos[0] += -400
        self.image = image
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(topleft = self.pos)

    def update(self, player_pos):
        pass
