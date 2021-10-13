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

        self.backbutton = MenuButton(canvas, (100, 150), "Pop Phase",
            command=self.exit_phase)

        self.tiles = pygame.sprite.Group()
        self.place_tiles()

        self.player = Player((300,300))

    def update(self, dt):
        self.player.update(self.listener, dt)
        self.tiles.update(self.player.pos)
        self.backbutton.update(self.listener)

    def render(self):
        self.tiles.draw(self.canvas)
        self.player.render(self.canvas)

    def place_tiles(self):
        with open(os.path.join(_base_dir, "temp_world.json")) as f:
            data = json.load(f)
        for r, row in enumerate(data["map"]):
            for c, tile in enumerate(row):
                if tile == 1:
                    self.tiles.add(Tile((c,r), tile_frames[4]))

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, listener, canvas):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.listener = listener
        self.canvas = canvas
        self.image = pygame.image.load(os.path.join(sprite_dir, "mike.png"))
        self.rect = self.image.get_rect(topleft = self.pos)

<<<<<<< Updated upstream
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 5

    def update(self, listener, dt):
        self.movement(listener, dt)
=======
    def update(self, dt):
        self.movement(dt)
>>>>>>> Stashed changes

    def render(self):
        self.canvas.blit(self.image, self.pos.xy)

    def movement(self, listener, dt):
        if listener.key_pressed("a", hold=True):
            print("dpws")
            self.velocity.x = -self.speed
        if listener.key_pressed("d", hold=True):
            print("dpws")
            self.velocity.x = self.speed

        if listener.key_up("a") or listener.key_up("d"):
            print("up")
            self.velocity.x = 0

        self.pos.x += self.velocity.x
        self.pos.y += self.velocity.y
        

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.size = (100,100)
        self.pos = [pos[0]*self.size[0], pos[1]*self.size[1]]
        self.offset = -400
        self.pos[0] += self.offset
        self.image = image
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(topleft = self.pos)

    def update(self, player_pos):
        self.offset += player_pos.x
        self.pos[0] = self.offset
        self.rect.x = self.pos[0]
