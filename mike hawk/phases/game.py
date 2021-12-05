import pygame, sys, copy
sys.path.append("..")

from .phase import Phase
from res.widgets import MenuButton
from res.animator import Animator
from res.timers import Timer

import json, os
from res.config import _base_dir, sprite_dir, game_vars, paralax_layers, player_animations, MAX_Y, colors
from res.tileset import load_set


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


class Camera:
    def __init__(self, game, canvas):
        self.game = game
        self.player = game.player
        
        self.CANVAS_W, self.CANVAS_H = canvas.get_size()
        self.MIDDLE = pygame.Vector2(self.CANVAS_W/2, self.CANVAS_H/2)

        self.offset = pygame.Vector2(0,0)
        self.total_offset = pygame.Vector2(0,0)
        self.current_bound = pygame.Vector2(self.game.max_x*game_vars["tile_size"]-self.CANVAS_W, MAX_Y*game_vars["tile_size"]-self.CANVAS_H)
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

        if self.abs_y > self.current_bound.y:
            self.offset.y -= self.abs_y - self.current_bound.y
            self.total_offset.y = self.current_bound.y
 

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
        self.previous_state = None
        self.state_history = []
        self.facing = {"left":False, "right":True}
        self.enable_jump = False
        
        # Timers
        self.idle_timer = Timer("down", "ticks", 2)
        self.jump_hold_timer = Timer("down", "ticks", 15)

        self.acceleration = pygame.Vector2(0, game_vars["gravity"])
        self.velocity = pygame.Vector2(0, 0)
        self.scroll_offset = pygame.Vector2(0, 0)
        self.animator = Animator(self.frames, 0.2)

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
            self.previous_state = self.state.copy()

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

            if self.find_true(self.state) != self.find_true(self.previous_state):
                for key, value in self.state.items():
                    if value == True:
                        self.state_history.append(key)
                if len(self.state_history) > 4:
                    self.state_history.pop(0)

        if debug:
            state = self.find_true(self.state)
            if state != None:
                #print(state, " : ", self.state_history)
                pass

    def update(self, dt, collisions_objects, scroll):

        self.check_idle()
        self.check_state(True)

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
        dt = 1
        self.check_state()

        key_a = self.listener.key_pressed("a", hold=True)
        key_d = self.listener.key_pressed("d", hold=True)
        direction = key_d - key_a
        if direction == 1:
            self.facing["left"], self.facing["right"] = False, True 
        if direction == -1:
            self.facing["left"], self.facing["right"] = True, False

        #if self.previous_state["running"] and self.state["jumping"]:
            """
            Note to self
            # Fix previous state so the determination of wheter or not
            # toggle sprint is on. (max vel should only increase if
            # running before jumping)
            # previous state cant be None? 
            # Friction in air should be less than on ground but the amount
            # you can move the character way less.
            # """
            #pass


        if any([self.state["running"], self.state["jumping"], self.state["falling"]]):
            toggle_sprint = game_vars["sprint_multiplier"]**self.state["running"]
            velocity_cap_multiplier = game_vars["sprint_multiplier"]
        else:
            toggle_sprint = 1
            velocity_cap_multiplier = 1
        
        if self.collisions["bottom"]:
            friction = game_vars["ground_friction"]
        else:
            friction = game_vars["air_resistance"]

        self.acceleration.x = game_vars["speed"]*direction*toggle_sprint
        self.velocity.x += dt*(self.acceleration.x + self.velocity.x*friction)
        self.limit_velocity(game_vars["max_vel"]*velocity_cap_multiplier)
        self.pos.x += int(self.velocity.x*dt + 0.5*(self.acceleration.x * dt**2))

        self.rect.centerx = self.pos.x

    def vertical_movement(self, dt):
        dt *= 60
        dt = 1
        self.check_state()
        if self.listener.key_pressed("space", hold=True):
            if self.collisions["bottom"] == True and self.enable_jump:
                self.velocity.y = -game_vars["jump strength"]
                self.enable_jump = False
                self.jump_hold_timer.start()

            elif self.jump_hold_timer.finished():
                self.jump_hold_timer.reset()

            elif self.jump_hold_timer.running:
                self.velocity.y = -game_vars["jump strength"]

        elif self.listener.key_up("space"):
            self.jump_hold_timer.reset()

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
            try:
                if self.state_history[-1] != "idle":
                    self.state_history.append("idle")
            except IndexError:
                pass

    
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

    def find_true(self, dictionary):
        for key, value in dictionary.items():
            if value == True:
                return key



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
        
        