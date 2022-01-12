import pygame, sys, math
sys.path.append("..")

from phases.game.game_res.camera import Camera, Paralax
from phases.game.game_res.entities.player import Player

from phases.phase import Phase
from res.widgets import MenuButton

import json, os
from res.config import _base_dir, sprite_dir, game_vars, paralax_layers, player_animations, MAX_Y, colors
from res.tileset import load_set


# Return the angle between two points
def get_angle(pos1, pos2):
    delta_y = pos1[1] - pos2[1]
    delta_x = pos1[0] - pos2[0]
    angle = math.degrees(math.atan2(delta_y, delta_x))
    angle = angle if angle >= 0 else 360 + angle
    return angle

class Game(Phase):
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

        tileset = list(load_set(sprite_dir, self.level["tileset"]).values())
        self.load_map(tileset)
        self.paralax = Paralax(canvas, paralax_layers)

        player_dim = (int(self.tile_size*1.5), int(self.tile_size*3))
        spawn_x, spawn_y = self.level["spawn"]
        self.player = Player(listener, canvas, (spawn_x*self.tile_size, spawn_y*self.tile_size), player_dim)
        
        self.camera = Camera(self, canvas)
        self.scroll = pygame.Vector2(0, 0)

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


    def render(self):
        self.paralax.render(method = "bg")
        self.tiles.draw(self.canvas)
        self.other_tiles.draw(self.canvas)
        self.bullets.draw(self.canvas)
        self.player.render()
        self.backbutton.update()
        self.paralax.render(method = "fg")

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


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size, image):
        super().__init__()
        self.size = size, size
        self.pos = pygame.Vector2(pos[0]*self.size[0], pos[1]*self.size[1])
        self.image = image
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(topleft = self.pos)
        self.scroll_offset = pygame.Vector2(0, 0)

    @property
    def abs_x(self):
        return self.pos.x + self.scroll_offset.x

    @property
    def abs_y(self):
        return self.pos.y - self.scroll_offset.y

    def update(self, scroll):
        self.scroll_offset += scroll
        self.pos.x += -(scroll.x)
        self.pos.y += -(scroll.y)

        self.rect.topleft = self.pos.xy


class Trigger(pygame.sprite.Sprite):
    def __init__(self, pos, command, type):
        super().__init__()
        self.command, self.type = command, int(type)

        size = game_vars["tile_size"]
        self.pos = pygame.Vector2(pos[0]*size, pos[1]*size)
        self.rect = pygame.Rect(self.pos.xy, (size, size))

        self.player_in_trigger = False

    def update(self, scroll):
        self.pos.x -= scroll.x
        self.pos.y -= scroll.y

        self.rect.topleft = self.pos.xy


class TriggerType:
    def __init__(self, command, type, mesh):
        self.command, self.type, self.mesh = command, type, mesh
        self.triggerd = False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle: int, speed: int):
        super().__init__()
        self.angle = math.radians(angle)
        self.speed = speed
        
        temp_size = 20
        self.rect = pygame.Rect(pos, (20, 20))
        self.image = pygame.Surface((temp_size, temp_size))
        self.image.fill(colors["black"])


    def update(self, scroll, tiles):
        self.rect.x += math.cos(self.angle) * self.speed - scroll.x
        self.rect.y += math.sin(self.angle) * self.speed - scroll.y
        if pygame.sprite.spritecollide(self, tiles, dokill=True):
            self.kill()


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

        