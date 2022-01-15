import pygame, sys, math
sys.path.append("..")

from phases.game.game_res.camera import Camera, Paralax
from phases.game.game_res.map import Tile, Trigger, TriggerType
from phases.game.game_res.entities.player import Player

from phases.phase import Phase
from res.widgets import MenuButton

import json, os
from res.config import _base_dir, spritesheet_dir, game_vars, paralax_layers, colors, bounding_boxes
from res.tileset import load_set

from phases.game.game_res.entities.player import Player
from phases.game.game_res.entities.bullet import Bullet
from phases.game.game_res.entities.enemies import Enemy

class Game(Phase):
    """
    
    """
    def __init__(self, canvas, listener, level):
        self.canvas = canvas
        self.listener = listener
        
        self.backbutton = MenuButton(canvas, listener, (100, 150), "Back",
            command=self.exit_phase)
        self.tiles = pygame.sprite.Group()
        self.other_tiles = pygame.sprite.Group()
        self.triggers = pygame.sprite.Group()
        self.tile_size = game_vars["tile_size"]

        self.bullets = pygame.sprite.Group()

        with open(os.path.join(_base_dir, "levels", f"{level}.json")) as f:
            self.level = json.load(f)
        self.map = self.level["map"]

        print(self.level["tileset"])

        tileset = list(load_set(os.path.join(spritesheet_dir, "old tiles"), self.level["tileset"]).values())
        self.load_map(tileset)
        self.paralax = Paralax(canvas, paralax_layers)

        player_height = int(self.tile_size*2)
        spawn_x, spawn_y = self.level["spawn"]
        self.player = Player(listener, canvas, (spawn_x*self.tile_size, spawn_y*self.tile_size), player_height)
        
        self.camera = Camera(self, canvas)
        self.scroll = pygame.Vector2(0, 0)

        self.enemy_group = pygame.sprite.Group()
        self.enemy_group.add(Enemy((3, 5)))
        

    def load_map(self, tileset):
        x_list = []
        for pos, tile_data in self.map.items():
            index, layer = tile_data
            tile = Tile([int(i) for i in pos.split(", ")], self.tile_size, tileset[layer][index])
            if layer == 0:
                self.tiles.add(tile)
            elif layer == 1:
                self.other_tiles.add(tile)
            x_list.append(int(pos.split(", ")[0]))
        self.max_x = max(x_list) + 1

        for trigger in self.level["triggers"]:
            self.triggers.add(Trigger(trigger["pos"], 
                *self.level["register"][trigger["name"]])
            )

    def update(self, dt, *args, **kwargs):
        self.scroll = self.camera.get_offset()
        self.player.update(dt, self.tiles, self.scroll)
        self.limit_player()
        self.other_tiles.update(self.scroll)
        self.tiles.update(self.scroll)
        self.triggers.update(self.scroll)
        self.update_triggers()
        self.paralax.update(self.scroll)
        #print(get_angle(pygame.mouse.get_pos(), self.player.rect.center))
        if self.listener.mouse_clicked(1, hold=True, trigger=20, id="player_shoot_bullet_1"):
            angle = get_angle(pygame.mouse.get_pos(), self.player.rect.center)
            self.bullets.add(Bullet(self.player.rect.center, angle, 20)) # player.current weapon
            print(angle, math.cos(angle), math.sin(angle))
        self.bullets.update(self.scroll, self.tiles)
        Tile.tiles = self.tiles
        self.enemy_group.update(self.player.pos)


    def render(self):
        self.paralax.render(method = "bg")
        self.tiles.draw(self.canvas)
        self.other_tiles.draw(self.canvas)
        self.bullets.draw(self.canvas)
        self.player.render()
        self.backbutton.update()
        self.paralax.render(method = "fg")
        self.enemy_group.draw(self.canvas)

    def get_world_dimensions(self):
        return (len(self.map[0]) * self.tile_size, len(self.map) * self.tile_size)

    def limit_player(self):
        if self.player.rect.right > self.canvas.get_width():
            self.player.rect.right = self.canvas.get_width()
        if self.player.rect.left < 0:
            self.player.rect.left = 0

        self.player.pos.xy = self.player.rect.midbottom

    def update_triggers(self):
        collisions = pygame.sprite.spritecollide(self.player, self.triggers, False)
        for trigger in self.triggers:
            if trigger in collisions:
                if trigger.type == 0:
                    exec(trigger.command)
                    trigger.kill()
                elif trigger.type == 1:
                    if not trigger.player_in_trigger:
                        exec(trigger.command)
                    trigger.player_in_trigger = True
                elif trigger.type == 2:
                    exec(trigger.command)
            else:
                trigger.player_in_trigger = False

    def kill(self):
        print("killed player")  

# Return the angle between two points
def get_angle(pos1, pos2):
    delta_y = pos1[1] - pos2[1]
    delta_x = pos1[0] - pos2[0]
    angle = math.degrees(math.atan2(delta_y, delta_x))
    angle = angle if angle >= 0 else 360 + angle
    return angle 