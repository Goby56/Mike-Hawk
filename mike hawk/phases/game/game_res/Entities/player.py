import pygame, sys, os
sys.path.append("..")
from res.config import spritesheet_dir, game_vars, player_animations, bounding_boxes, colors, fps, debug
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

        drawbox_scaling = pbox["drawbox"].elementwise()/pbox["hitbox"].elementwise()
        drawbox_dim = scaled_hitbox.elementwise()*drawbox_scaling.elementwise()

        self.rect = pygame.Rect((0,0), scaled_hitbox)
        self.rect.midbottom = self.pos.xy

        self.drawbox = pygame.Rect((0,0), drawbox_dim)
        self.drawbox.midbottom = self.pos.xy

        for tag in self.spritesheet.frames.keys():
            for i, frame in enumerate(self.spritesheet.frames[tag]):
                self.spritesheet.frames[tag][i] = pygame.transform.scale(frame, (int(drawbox_dim.x), int(drawbox_dim.y)))

        # Tags
        self.collisions = {"right":False, "left":False, "top":False, "bottom":False}
        self.state = {
            "idle":False, "running":False, "jumping":False, "falling":False, 
            "rolling":False, "death":False
            }
        self.animation_state = {
            "rolling":False, "death":False, "jump":False,
            "whip_slash":False, "whip_stun":False, "fire_pistol":False
            } # Animations that should play all the way through
        self.previous_state = self.state.copy()
        self.state_history = []
        self.facing = {"left":False, "right":True}
        self.fell_from_height = 0
        
        # Timers
        self.idle_timer = Timer("down", "ticks", 2)
        rolling_animation_duration = sum(self.animator.animation_delays["rolling"])-1
        self.rolling_animation_timer = Timer("down", "ticks", rolling_animation_duration)
        death_animation_duration = sum(self.animator.animation_delays["death"])
        self.death_animation_timer = Timer("down", "ticks", death_animation_duration)

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

    @property
    def fall_distance(self):
        return -(self.abs_y-self.fell_from_height)/game_vars["tile_size"]

    def update(self, dt, collisions_objects, scroll):
        self.check_state()
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
        history = self.state_history[::-1]
        if self.state["running"] and abs(self.velocity.x) > 0.25*game_vars["max_vel"]:
            frame = self.animator.get_frame("running")
        elif self.state["jumping"]:
            frame = self.animator.get_frame("jumping")
        elif self.state["falling"]:
            frame = self.animator.get_frame("falling")
        elif len(history) >= 2 and self.find_true(self.state) == None and history[0] == "jumping":
            frame = self.animator.get_frame("jumping")
        elif len(history) >= 2 and self.find_true(self.state) == None and history[0] == "falling":
            frame = self.animator.get_frame("running")
        elif self.state["rolling"]:
            time = self.rolling_animation_timer.get_time()
            frame = self.animator.get_frame("rolling")
        elif self.state["death"]:
            frame = self.animator.get_frame("death")
        else:
            frame = self.animator.get_frame("idle")

        if self.velocity.x < -game_vars["max_vel"]*0.25 or self.facing["left"]:
            frame = pygame.transform.flip(frame, True, False)
        
        self.canvas.blit(frame, self.drawbox.topleft)

        pygame.draw.rect(self.canvas, colors["cool blue"], self.drawbox, width=1)
        pygame.draw.rect(self.canvas, colors["red"], self.rect, width=1)

    def set_state(self, state, bool=True, animation=False):
        """
        Sets all states to false, then {state} to true
        Can set the given {state} to false if {bool}=False
        If {animation}=True the given {state} will become true in the {self.animation_state}
        """
        if animation:
            for key in self.animation_state.keys():
                self.animation_state[key] = False
            if state != None:
                self.animation_state[state] = bool
        else:
            for key in self.state.keys():
                self.state[key] = False
            if state != None:
                self.state[state] = bool

    def check_state(self, debug=False):
        if not debug:
            self.previous_state = self.state.copy()

            if self.rolling_animation_timer.finished():
                self.set_state("rolling", bool=False, animation=True)
                self.set_state("rolling", bool=False)
                self.rolling_animation_timer.reset()
            
            if self.death_animation_timer.finished():
                self.set_state("death", bool=False, animation=True)
                self.set_state("death", bool=False)
                self.rolling_animation_timer.reset()

            if self.animation_state["rolling"]:
                self.set_state("rolling")
            elif self.animation_state["death"]:
                self.set_state("death")
            elif self.collisions["bottom"] and (self.state["falling"] or self.previous_state["falling"]):
                rolling_fall_range = range(game_vars["fall_ranges"][0], game_vars["fall_ranges"][1])
                if int(self.fall_distance) in rolling_fall_range:
                    self.set_state("rolling")
                    self.set_state("rolling", animation=True)
                    self.rolling_animation_timer.start()
                elif int(self.fall_distance) >= max(rolling_fall_range):
                    self.set_state("death")
                    self.set_state("death", animation=True)
                    self.death_animation_timer.start()
                    self.death_animation_timer.start()
                else:
                    self.set_state(None)
            elif self.collisions["bottom"] and self.velocity.x != 0:
                self.set_state("running")
            elif self.velocity.y < 0:
                self.set_state("jumping")
            elif self.velocity.y > 0:
                self.set_state("falling")
            else:
                self.set_state(None)

            if self.find_true(self.state) != self.find_true(self.previous_state):
                if self.state["falling"]:
                    self.fell_from_height = self.abs_y
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

    def horizontal_movement(self, dt):
        if debug:
            dt = 1
        else: dt *= fps

        key_a = self.listener.key_pressed("a", hold=True)
        key_d = self.listener.key_pressed("d", hold=True)
        direction = key_d - key_a
        if direction == 1:
            self.facing["left"], self.facing["right"] = False, True 
        if direction == -1:
            self.facing["left"], self.facing["right"] = True, False

        if self.state["rolling"]:
            if self.facing["right"]:
                direction = 0.15
            elif self.facing["left"]:
                direction = -0.15
    
            """
            # Friction in air should be less than on ground but the amount
            # you can move the character way less.
            """
        
        if self.collisions["bottom"]:
            friction = game_vars["ground_friction"]
        else:
            friction = game_vars["air_resistance"]

        self.acceleration.x = game_vars["speed"]*direction
        self.velocity.x += dt*(self.acceleration.x + self.velocity.x*friction)
        self.limit_velocity(game_vars["max_vel"])
        self.pos.x += int(self.velocity.x*dt + 0.5*(self.acceleration.x * dt**2))

        self.rect.centerx = self.pos.x
        self.drawbox.centerx = self.pos.x

    def vertical_movement(self, dt):
        if debug:
            dt = 1
        else: dt *= fps

        if self.listener.key_pressed("space", hold=True) and self.collisions["bottom"]:
            self.velocity.y = -game_vars["jump strength"]

        self.collisions["bottom"] = False

        self.velocity.y += self.acceleration.y*dt
        self.pos.y += int(self.velocity.y*dt + 0.5*(self.acceleration.y * dt**2))   
        
        self.rect.bottom = self.pos.y
        self.drawbox.bottom = self.pos.y

    def limit_velocity(self, max_velocity, increase_vel=False):
        if increase_vel == True: max_velocity *= game_vars["sprint_multiplier"]
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
        return None