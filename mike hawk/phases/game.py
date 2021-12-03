import pygame, sys
sys.path.append("..")

from .phase import Phase
from res.widgets import MenuButton
from res.animator import Animator
from res.timers import Timer

import json, os
from res.config import _base_dir, sprite_dir, game_vars, paralax_layers, player_animations
from res.tileset import load_set


class Game(Phase):
    def __init__(self, canvas, listener, level):
        self.canvas = canvas
        self.listener = listener
        
        self.backbutton = MenuButton(canvas, listener, (100, 150), "Back",
            command=self.exit_phase)
        self.tiles = pygame.sprite.Group()
        self.other_tiles = pygame.sprite.Group()
        self.tile_size = game_vars["tile_size"]

        with open(os.path.join(_base_dir, "levels", f"{level}.json")) as f:
            self.level = json.load(f)
        self.map = self.level["map"]

        tileset = load_set(sprite_dir, self.level["tile set"])
        self.place_tiles(tileset)
        self.paralax = Paralax(canvas, paralax_layers)

        world_height = self.get_world_dimensions()[1]
        player_dim = (int(self.tile_size*1.5), int(self.tile_size*3))
        spawn = (self.level["spawn"][0]*self.tile_size - player_dim[0]//2, 
            world_height - self.level["spawn"][1]*self.tile_size - player_dim[1])
        self.player = Player(listener, canvas, spawn, player_dim)
        
        self.camera = Camera(self, canvas)
        self.scroll = pygame.Vector2(0, 0)

    def place_tiles(self, tileset):
        for r, row in enumerate(self.map):
            for c, tile in enumerate(row):
                if tile[0]:
                    new_tile = Tile((c,r), self.tile_size, tileset[tile[1]][tile[0]-1])
                    if tile[1] == "fg":
                        self.tiles.add(new_tile)
                    else:
                        self.other_tiles.add(new_tile)

    def update(self, dt, *args, **kwargs):
        self.scroll = self.camera.get_offset()
        self.player.update(dt, self.tiles, self.scroll)
        self.limit_player()
        self.other_tiles.update(self.scroll)
        self.tiles.update(self.scroll)
        self.paralax.update(self.scroll)

    def render(self):
        self.paralax.render(method = "bg")
        self.tiles.draw(self.canvas)
        self.other_tiles.draw(self.canvas)
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

    def kill(self):
        print("killed player")


class Camera:
    def __init__(self, game, canvas):
        self.game = game
        self.player = game.player
        
        self.CANVAS_W, self.CANVAS_H = canvas.get_size()
        self.MIDDLE = pygame.Vector2(self.CANVAS_W/2, self.CANVAS_H/2)

        self.offset = pygame.Vector2(0,0)
        self.total_offset = pygame.Vector2(0,0)
        self.current_bound = pygame.Vector2(700, 0)
        # Offset for follow method
        self.method = "follow"
    
    @property
    def abs_x(self):
        return self.total_offset.x

    @property
    def abs_y(self):
        return self.total_offset.y

    def get_offset(self):
        exec(f"self.{self.method}()")
        return self.offset

    def follow(self):
        self.offset.x += (self.player.pos.x - self.offset.x - self.MIDDLE.x)
        self.offset.y += (self.player.pos.y - self.offset.y - self.MIDDLE.y - self.player.height)
        self.total_offset += self.offset
        self.border()

    def border(self):
        if self.abs_x < 0:
            self.offset.x += abs(self.abs_x)
            self.total_offset.x = 0

        if self.abs_x > self.current_bound.x:
            self.offset.x -= self.abs_x - self.current_bound.x
            self.total_offset.x = self.current_bound.x

        print(self.abs_x, self.offset.x)

        if self.abs_y < 0:
            self.offset.y = 0
            self.total_offset.y = 0

        world_dim = self.game.get_world_dimensions()
        if self.abs_x > world_dim[0] - 2*self.MIDDLE.x:
            self.offset.x = 0
            self.total_offset.x = world_dim[0] - 2*self.MIDDLE.x

        if self.abs_y > world_dim[1] - 2*self.MIDDLE.y:
            self.offset.y = 0
            self.total_offset.y = world_dim[1] - 2*self.MIDDLE.y

    def auto(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, listener, canvas, pos, size):
        super().__init__()
        self.listener = listener
        self.canvas = canvas
        self.pos = pygame.Vector2(pos)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(sprite_dir, "player_idle.png")), size)
        self.frames = player_animations
        for i, frame in enumerate(self.frames):
            self.frames[i] = pygame.transform.scale(frame, size)
        self.width, self.height = self.image.get_width(), self.image.get_height()
        self.rect = self.image.get_rect(midbottom=self.pos)

        # Tags
        self.collisions = {"right":False, "left":False, "top":False, "bottom":False}
        self.state = {"idle":False, "walking":False, "jumping":False, "running":False, "falling":False, "charging":False}
        self.facing = {"left":False, "right":True}
        self.enable_jump = False
        self.enable_jump_boost = False
        
        # Timers
        self.idle_timer = Timer("down", "ticks", 1)
        self.jump_hold_timer = Timer("down", "ticks", 10)
        self.jump_boost_distribution_timer = Timer("up", "ticks", 10)

        self.acceleration = pygame.Vector2(0, game_vars["gravity"])
        self.velocity = pygame.Vector2(0, 0)
        self.scroll_offset = pygame.Vector2(0, 0)
        self.animator = Animator(self.frames, 0.2)
        self.durations = {"space":0}

    @property
    def abs_x(self):
        return self.pos.x + self.scroll_offset.x

    @property
    def abs_y(self):
        return self.pos.y - self.scroll_offset.y

    def set_state(self, state, bool=True):
        for key in self.state.keys():
            self.state[key] = False
        if state != None:
            self.state[state] = bool

    def check_state(self, debug=False):
        if not debug:
            if self.velocity.x != 0 and self.collisions["bottom"]:
                if self.listener.key_pressed("left shift", hold=True):
                    self.set_state("running")
                else:
                    self.set_state("walking")
            else:
                self.set_state(None)

            if self.velocity.y < 0:
                self.set_state("jumping")
            elif self.velocity.y > game_vars["gravity"]:
                self.set_state("falling")

        if debug:
            for key, value in self.state.items():
                if value:
                    print(key)


    def update(self, dt, collisions_objects, scroll):

        self.check_idle()

        self.horizontal_movement(dt)
        self.handle_collisions(self.get_collisions(collisions_objects), axis=0)
        self.vertical_movement(dt)
        self.handle_collisions(self.get_collisions(collisions_objects), axis=1)
        
        self.scroll_offset += scroll
        self.pos.x += -(scroll.x)
        self.pos.y += -(scroll.y)

        self.rect.midbottom = self.pos.xy

    def render(self):
        if abs(self.velocity.x) > game_vars["max_vel"]*0.25:
            frame = self.animator.get_frame()
            if self.velocity.x < 0:
                frame = pygame.transform.flip(frame, True, False)
        else:
            frame = self.image
            if self.facing["left"]:
                frame = pygame.transform.flip(frame, True, False)
        self.canvas.blit(frame, self.rect.topleft)

    def horizontal_movement(self, dt):
        dt *= 60
        self.check_state()

        key_a = self.listener.key_pressed("a", hold=True)
        key_d = self.listener.key_pressed("d", hold=True)
        direction = key_d - key_a
        if direction == 1:
            self.facing["left"], self.facing["right"] = False, True 
        if direction == -1:
            self.facing["left"], self.facing["right"] = True, False

        if any([self.state["running"], self.state["jumping"], self.state["falling"]]):
            velocity_multiplier = game_vars["sprint_multiplier"]**self.state["running"]
            velocity_cap_multiplier = game_vars["sprint_multiplier"]
        else:
            velocity_multiplier = 1
            velocity_cap_multiplier = 1
            
        self.acceleration.x = game_vars["speed"]*direction*velocity_multiplier
        self.velocity.x += dt*(self.acceleration.x + self.velocity.x*game_vars["friction"])
        self.limit_velocity(game_vars["max_vel"]*velocity_cap_multiplier)
        self.pos.x += int(self.velocity.x*dt + 0.5*(self.acceleration.x * dt**2))

        self.rect.centerx = self.pos.x

    def vertical_movement(self, dt):
        dt *= 60
        
        # Fix so that you dont jump when pressing a or d while charging
        # Have it so that you look left or right instead
        # Otherwise execute charged jump when pressing a or d

        self.check_state()

        if self.listener.key_pressed("space", hold=True):
            if self.collisions["bottom"] == True and self.enable_jump:
                self.velocity.y = -game_vars["jump strength"]
                self.enable_jump = False
                self.enable_jump_boost = True
                self.jump_hold_timer.start()
            
            elif self.jump_hold_timer.finished():
                self.jump_boost_distribution_timer.start()
                self.jump_hold_timer.reset()

            elif self.enable_jump_boost and self.jump_boost_distribution_timer.running:
                distribution = 1/self.jump_boost_distribution_timer.requirement
                amplifier = game_vars["jump_amplifier"]*distribution
                self.velocity.y += -game_vars["jump strength"]*(amplifier-1)
                print(amplifier)

        elif self.listener.key_up("space"):
            self.enable_jump_boost = False
            self.jump_hold_timer.reset()
            self.jump_boost_distribution_timer.reset()
    

        self.collisions["bottom"] = False

        self.velocity.y += self.acceleration.y*dt
        self.pos.y += int(self.velocity.y*dt + 0.5*(self.acceleration.y * dt**2))   
        
        self.rect.bottom = self.pos.y

    def limit_velocity(self, max_velocity):
        if abs(self.velocity.x) > max_velocity:
            self.velocity.x = max_velocity if self.velocity.x > 0 else -max_velocity 
        if abs(self.velocity.x) < 0.1: self.velocity.x = 0

    def check_idle(self):
        if not any(self.state.values()):
            self.idle_timer.start()
        else:
            self.idle_timer.reset()

        if self.idle_timer.finished():
            self.set_state("idle")
            self.idle_timer.reset()
    
    def handle_collisions(self, tile_collisions, axis):
        if tile_collisions:
            for tile in tile_collisions:
                if axis == 0:
                    if self.velocity.x > 0: 
                        self.rect.right = tile.rect.left
                        self.velocity.x = 0
                        self.collisions["right"] = True
                    elif self.velocity.x < 0: 
                        self.rect.left = tile.rect.right
                        self.velocity.x = 0
                        self.collisions["left"] = True
                elif axis == 1:
                    if self.velocity.y > 0:
                        self.rect.bottom = tile.rect.top
                        self.velocity.y = 0
                        self.collisions["bottom"] = True
                        self.enable_jump = True
                    elif self.velocity.y < 0: 
                        self.rect.top = tile.rect.bottom
                        self.velocity.y = 0
                        self.collisions["top"] = True
            self.pos.xy = self.rect.midbottom

    def get_collisions(self, group):
        collisions = pygame.sprite.spritecollide(self, group, False)
        return collisions


class Paralax:
    def __init__(self, canvas, layers):
        self.layers = [[image, [0,0]] for image in layers]
        for i, layer in enumerate(self.layers):
            self.layers[i][0] = pygame.transform.scale(layer[0], canvas.get_size())
        self.canvas = canvas
        self.total_scroll_x = 0
    
    def update(self, scroll):
        self.total_scroll_x += scroll.x
        for i in range(len(self.layers)-1):
            layer_offset = -self.total_scroll_x*(i+1)**2/50
            index = -layer_offset//self.canvas.get_width()
            self.layers[1:][i][1][0] = layer_offset 
            self.layers[1:][i][1][0] += index*self.canvas.get_width()
        
    def render(self, method):
        if method == "bg":
            for layer in self.layers:
                x = layer[1][0]
                y = layer[1][1]
                self.canvas.blit(layer[0], (x, y))
                self.canvas.blit(layer[0], (x+self.canvas.get_width(), y))
                self.canvas.blit(layer[0], (x-self.canvas.get_width(), y))
        

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