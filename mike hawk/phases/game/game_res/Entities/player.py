import pygame, sys, os
sys.path.append("..")
from res.config import spritesheet_dir, game_vars, player_animations, bounding_boxes, colors
from res.animator import Animator
from res.timers import Timer
from res.spritesheet import Spritesheet


class Player(pygame.sprite.Sprite):
    """
    pos: Position of where the player first spawns
    height: The height of the player measured in X tiles (pixels)
    """
    def __init__(self, listener, canvas, pos, height):
        super().__init__()
        self.listener = listener
        self.canvas = canvas
        self.pos = pygame.Vector2(pos)
        self.height = height

        # Class instantiations
        self.spritesheet = Spritesheet("jones_hawk")
        self.animator = Animator("jones_hawk", starting_animation="idle")
        
        # Rects and image scaling
        pbox = bounding_boxes["player"] # Player boxes
        hitbox_wh_ratio = pbox["hitbox"].x/pbox["hitbox"].y # Drawbox width/height ratio
        scaled_hitbox = pygame.Vector2(height*hitbox_wh_ratio, height) # Scale image to these dimensions

        self.rect = pygame.Rect((0,0), scaled_hitbox)
        self.rect.midbottom = self.pos.xy

        drawbox_scaling = pbox["drawbox"].elementwise()/pbox["hitbox"].elementwise()
        drawbox_dim = scaled_hitbox.elementwise()*drawbox_scaling.elementwise()

        for tag in self.spritesheet.frames.keys():
            for i, frame in enumerate(self.spritesheet.frames[tag]):
                self.spritesheet.frames[tag][i] = pygame.transform.scale(frame, (int(drawbox_dim.x), int(drawbox_dim.y)))

        self.drawbox = pygame.Rect((0,0), drawbox_dim)
        self.drawbox.midbottom = self.pos.xy

        # # Rects and image scaling
        # pbox = bounding_boxes["player"] # Player boxes
        # drawbox_wh_ratio = pbox["drawbox"].x/pbox["drawbox"].y # Drawbox width/height ratio
        # scaled_dim = pygame.Vector2(height*drawbox_wh_ratio, height) # Scale image to these dimensions

        # for tag in self.spritesheet.frames.keys():
        #     for i, frame in enumerate(self.spritesheet.frames[tag]):
        #         self.spritesheet.frames[tag][i] = pygame.transform.scale(frame, (int(scaled_dim.x), int(scaled_dim.y)))

        # self.drawbox_scaling = scaled_dim.elementwise()/pbox["drawbox"].elementwise()
        # self.drawbox = pygame.Rect((0,0), scaled_dim)
        # self.drawbox.midbottom = self.pos.xy

        # hitbox_scaling = pbox["hitbox"].elementwise()/pbox["drawbox"].elementwise()
        # hitbox_dim = scaled_dim.elementwise()*hitbox_scaling.elementwise()
        # self.rect = pygame.Rect((0,0), hitbox_dim)
        # self.rect.midbottom = self.pos.xy

        # Tags
        self.collisions = {"right":False, "left":False, "top":False, "bottom":False}
        self.state = {
            "idle":False, "walking":False, "running":False, 
            "jump":False, "jumping":False, "falling":False}
        self.animation_state = {
            "idle":False, "running":False, "rolling":False, 
            "whip_slash":False, "whip_stun":False, "fire_pistol":False, "death":False,
            "falling":False, "jump":False, "jumping":False
            }
        self.previous_state = None
        self.state_history = []
        self.facing = {"left":False, "right":True}
        self.enable_jump = False
        
        # Timers
        self.idle_timer = Timer("down", "ticks", 2)
        self.jump_hold_timer = Timer("down", "ticks", 15)

        # Other
        self.acceleration = pygame.Vector2(0, game_vars["gravity"])
        self.velocity = pygame.Vector2(0, 0)
        self.scroll_offset = pygame.Vector2(0, 0)

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
                print(state, " : ", self.state_history)
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
        self.drawbox.midbottom = self.pos.xy

    def render(self):
        if abs(self.velocity.x) > game_vars["max_vel"]*0.25:
            frame = self.animator.get_frame("running")
            if self.velocity.x < 0:
                frame = pygame.transform.flip(frame, True, False)
        else:
            frame = self.animator.get_frame("idle")
            if self.facing["left"]:
                frame = pygame.transform.flip(frame, True, False)
        self.canvas.blit(frame, self.drawbox.topleft)

        pygame.draw.rect(self.canvas, colors["cool blue"], self.drawbox, width=1)
        pygame.draw.rect(self.canvas, colors["red"], self.rect, width=1)

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

        increase_max_vel = False
        movement_modifier = 1
    
        if self.collisions["bottom"]:
            if abs(self.velocity.x) > 0:
                if self.listener.key_pressed("left shift", hold=True):
                    self.set_state("running")
            else:
                self.set_state("walking")
        
  
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
        
        if self.collisions["bottom"]:
            friction = game_vars["ground_friction"]
        else:
            friction = game_vars["air_resistance"]

        
        if self.state["running"]:
            movement_modifier = game_vars["sprint_multiplier"]
            increase_max_vel = True
        elif self.state["walking"]:
            movement_modifier = 1

        if len(self.state_history) >= 3:
            history = self.state_history[::-1]
            if history[0] == "falling" or history[0] == "jumping":
                if history[1] == "running" or history[2] == "running":
                    movement_modifier = game_vars["sprint_multiplier"]
                    increase_max_vel = True

        self.acceleration.x = game_vars["speed"]*direction*movement_modifier
        self.velocity.x += dt*(self.acceleration.x + self.velocity.x*friction)
        self.limit_velocity(game_vars["max_vel"], increase_max_vel)
        self.pos.x += int(self.velocity.x*dt + 0.5*(self.acceleration.x * dt**2))

        self.rect.centerx = self.pos.x
        self.drawbox.centerx = self.pos.x

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
        self.drawbox.bottom = self.pos.y

    def limit_velocity(self, max_velocity, increase_vel):

        if increase_vel == True: max_velocity *= game_vars["sprint_multiplier"]
        if abs(self.velocity.x) > max_velocity:
            self.velocity.x = max_velocity if self.velocity.x > 0 else -max_velocity 
        if abs(self.velocity.x) < 0.1: self.velocity.x = 0

    def check_idle(self):
        if not any(self.state.values()):
            self.idle_timer.start()
        else:
            self.idle_timer.reset()

        if self.idle_timer.finished() and self.collisions["bottom"]:
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
            self.drawbox.midbottom = self.pos.xy

    def get_collisions(self, group):
        collisions = pygame.sprite.spritecollide(self, group, False)
        return collisions

    def find_true(self, dictionary):
        for key, value in dictionary.items():
            if value == True:
                return key