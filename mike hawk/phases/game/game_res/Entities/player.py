import pygame, sys, os, math, json
sys.path.append("..")
from res.config import spritesheet_dir, _base_dir, game_vars, player_animations, bounding_boxes, colors, fps, debug
from res.animator import Animator
from res.timers import Timer
from res.spritesheet import Spritesheet
from .bullet import Bullet


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
        hitbox_dim = pygame.Vector2(height*hitbox_wh_ratio, height) # Scale image to these dimensions

        self.rect = pygame.Rect((0,0), hitbox_dim)
        self.rect.midbottom = self.pos.xy

        drawbox_scaling = pbox["drawbox"].elementwise()/pbox["hitbox"].elementwise()
        drawbox_dim = hitbox_dim.elementwise()*drawbox_scaling.elementwise()

        self.drawbox = pygame.Rect((0,0), drawbox_dim)
        self.drawbox.midbottom = self.pos.xy

        self.attack_range = (drawbox_dim.x-hitbox_dim.x)/2
        attackbox_dim = self.attack_range, hitbox_dim.y

        self.attackbox = pygame.Rect((0,0), attackbox_dim)
        self.attackbox.midleft = self.rect.midright

        for tag in self.spritesheet.frames.keys():
            for i, frame in enumerate(self.spritesheet.frames[tag]):
                self.spritesheet.frames[tag][i] = pygame.transform.scale(frame, (int(drawbox_dim.x), int(drawbox_dim.y)))

        # Tags
        self.collisions = {"right":False, "left":False, "top":False, "bottom":False}
        self.state = {
            "idle":False, "running":False, "jumping":False, "falling":False, 
            "rolling":False, "death":False, "attacking":False
            }
        self.animation_state = {
            "rolling":False, "death":False, "jump":False,
            "whip_slash":False, "whip_stun":False, "fire_pistol":False
            } # Animations that should play all the way through
        self.current_animation = "idle"
        self.previous_state = self.state.copy()
        self.state_history = []
        self.facing = {"left":False, "right":True}
        self.fell_from_height = 0
        with open(os.path.join(_base_dir, "player_animation_hierarchy.json"), "r") as f:
            self.animation_hierarchy = json.load(f)
        
        # Timers
        self.create_timers()

        # Other
        self.acceleration = pygame.Vector2(0, game_vars["gravity"])
        self.velocity = pygame.Vector2(0, 0)
        self.scroll_offset = pygame.Vector2(0, 0)
        self.current_attack_ability = "whip_slash"

    @property
    def abs_x(self):
        return self.pos.x + self.scroll_offset.x

    @property
    def abs_y(self):
        return self.pos.y - self.scroll_offset.y

    @property
    def fall_distance(self):
        return -(self.abs_y-self.fell_from_height)/game_vars["tile_size"]

    @property
    def mouse_pos(self):
        return pygame.Vector2(pygame.mouse.get_pos())

    def update(self, dt, collisions_objects, bullets, scroll):
        """
        Performs all the necessary updates for the player
        """
        self.global_bullets = bullets

        self.check_state()
        self.check_idle()
        self.check_state(debug=True)

        self.handle_input()

        self.horizontal_movement(dt)
        self.handle_collisions(self.get_collisions(collisions_objects), axis=0)
        self.vertical_movement(dt)
        self.handle_collisions(self.get_collisions(collisions_objects), axis=1)

        self.scroll_offset += scroll
        self.pos.x += -(scroll.x)
        self.pos.y += -(scroll.y)

        self.rect.midbottom = self.pos.xy
        self.drawbox.midbottom = self.pos.xy
        if self.facing["right"]:
            self.attackbox.midleft = self.rect.midright
        elif self.facing["left"]:
            self.attackbox.midright = self.rect.midleft

    def render(self):
        """
        Renders the correct frame depending on what state the player is 
        in with the help of the animator class.
        """
        if self.state["running"] and abs(self.velocity.x) > 0.25*game_vars["max_vel"]:
            frame = self.animator.get_frame("running")
        elif self.state["jumping"]:
            frame = self.animator.get_frame("jumping")
        elif self.state["falling"]:
            frame = self.animator.get_frame("falling")
        elif self.find_true(self.state) == None and self.get_state_from_history(0) == "jumping":
            frame = self.animator.get_frame("jumping")
        elif self.find_true(self.state) == None and self.get_state_from_history(0) == "jumping":
            frame = self.animator.get_frame("running")
        elif self.state["rolling"]:
            frame = self.animator.get_frame("rolling")
        elif self.state["death"]:
            frame = self.animator.get_frame("death")
        elif self.state["attacking"]:
            if self.animation_state["whip_slash"]:
                frame = self.animator.get_frame("whip_slash")
            elif self.animation_state["whip_stun"]:
                frame = self.animator.get_frame("whip_stun")
            elif self.animation_state["fire_pistol"]:
                frame = self.animator.get_frame("fire_pistol")
            else:
                frame = self.animator.get_frame("idle")
        else:
            frame = self.animator.get_frame("idle")

        if self.velocity.x < -game_vars["max_vel"]*0.25 or self.facing["left"]:
            frame = pygame.transform.flip(frame, True, False)
        
        self.canvas.blit(frame, self.drawbox.topleft)

        pygame.draw.rect(self.canvas, colors["cool blue"], self.drawbox, width=1)
        pygame.draw.rect(self.canvas, colors["red"], self.rect, width=1)
        pygame.draw.rect(self.canvas, colors["green"], self.attackbox, width=1)

    def set_state(self, state, bool=True, animation=False):
        """
        Sets all states to false, then {state} to true.
        Can set the given {state} to false if {bool}=False.
        If {animation}=True the given {state} will become true in the {self.animation_state}
        and stop some* of the animation timers\n
        *Do not stop\n
        -death_animation_timer
        """
        # if animation:
        #     for key in self.animation_state.keys():
        #         self.animation_state[key] = False
        #     if state != None:
        #         self.animation_state[state] = bool
        #     for animation in self.animation_timers:
        #         if animation not in [state, "death"]:
        #             self.animation_timers[animation].reset()
        # else:
        for key in self.state.keys():
            self.state[key] = False
        if state != None:
            self.state[state] = bool

    def append_animation(self, animation):
        self.animation_state[animation] = True

    def change_animation_to(self, animation):
        for state in self.animation_state.keys():
            self.animation_state[state] = False
        if animation != None:
            self.animation_state[animation] = True
            self.current_animation = animation

    def check_state(self, debug=False):
        """
        Determines what state the player is in and adds it to the state history if
        it is a new occurence of it.
        """
        if not debug:
            self.previous_state = self.state.copy()

            attack_animations = ["whip_slash", "whip_stun", "fire_pistol"]
            if any(self.animation_state.values()):
                pending_animations = []
                for state in self.animation_state.keys():
                    if self.animation_state[state] == True:
                        pending_animations.append(state)
                
                next_animation = ""
                for index in self.animation_hierarchy.keys():
                    ranking = self.animation_hierarchy[str(index)]
                    for animation in pending_animations:
                        if animation == ranking or (animation in attack_animations and ranking == "attacking"):
                            next_animation = animation
                            break
                    if next_animation != "":
                        break
                
                self.change_animation_to(next_animation)
                for timer in self.animation_timers.keys():
                    if timer == next_animation:
                        self.animation_timers[timer].start()
                        if self.animation_timers[timer].finished():
                            self.animation_timers[timer].reset()
                            self.change_animation_to(None)
                            if timer in ["rolling"]:
                                self.velocity.x = 0

                    else: self.animation_timers[timer].reset()

            if any(self.animation_state.values()):   
                for animation in self.animation_state.keys():
                    if self.animation_state[animation] == True:
                        if animation in attack_animations:
                            self.set_state("attacking")
                            self.velocity.x = 0
                        else: self.set_state(animation)

            elif self.collisions["bottom"] and self.velocity.x != 0:
                self.set_state("running")
            elif self.velocity.y < 0:
                self.set_state("jumping")
            elif self.velocity.y > game_vars["gravity"]:
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
        """
        Sets the player's state to idle if the idle timer has been reached 
        """
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

    def get_state_from_history(self, index):
        """
        Gets state from the history, index=0 is the current state
        """
        if len(self.state_history) > 3:
            return self.state_history[::-1][index]
        else: return False

    def handle_input(self):
        """
        Handles the player's inputs
        """
        # Shortcuts
        def key(key, hold=True): return self.listener.key_pressed(key, hold)
        def mouse(button, hold=True, trigger=1, id=""): return self.listener.mouse_clicked(button, hold, trigger, id)
        animation = self.animator.animation_delays[self.current_attack_ability]

        # Handle key inputs
        if key("1"):
            self.switch_attack("whip_slash")
            if self.attackbox.width > self.attack_range*0.90:
                self.attackbox.inflate_ip(-0.20*self.attack_range, 0)
        elif key("2"):
            self.switch_attack("whip_stun")
            if self.attackbox.width < self.attack_range*0.90:
                self.attackbox.inflate_ip(+0.20*self.attack_range, 0)
        elif key("3"):
            self.switch_attack("fire_pistol")

        # Handle mouse inputs
        if self.state["idle"]:
            if self.mouse_pos.x > self.pos.x:
                self.facing["left"], self.facing["right"] = False, True
            elif self.mouse_pos.x < self.pos.x:
                self.facing["left"], self.facing["right"] = True, False
        
        if mouse(1, hold=True, trigger=5*len(animation), id=self.current_attack_ability):
            self.attack(self.current_attack_ability)
        
    def horizontal_movement(self, dt):
        """
        Handles the player's horizontal movement
        """
        if debug:
            dt = 1
        else: dt *= fps

    
        key_a = self.listener.key_pressed("a", hold=True)
        key_d = self.listener.key_pressed("d", hold=True)

        direction = key_d - key_a

        if any(self.animation_state.values()):
            current_timer = self.animation_timers[self.find_true(self.animation_state)]
            if current_timer.get_time() > current_timer.starting_time*0.35:
                direction *= 0.15

        if direction == 1:
            self.facing["left"], self.facing["right"] = False, True 
        if direction == -1:
            self.facing["left"], self.facing["right"] = True, False

        if self.collisions["bottom"] and self.listener.key_pressed("left alt"):
            self.append_animation("rolling")
            self.rolling_animation_timer.start()

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
        """
        Handles the player's vertical movement
        """
        if debug:
            dt = 1
        else: dt *= fps

        if self.listener.key_pressed("space", hold=True) and self.collisions["bottom"]:
            self.velocity.y = -game_vars["jump strength"]

        if self.collisions["bottom"] and (self.state["falling"] or self.previous_state["falling"]):
            rolling_fall_range = range(game_vars["fall_ranges"][0], game_vars["fall_ranges"][1])
            if int(self.fall_distance) in rolling_fall_range:
                self.append_animation("rolling")
            elif int(self.fall_distance) >= max(rolling_fall_range):
                self.append_animation("death")

        self.collisions["bottom"] = False

        
        self.velocity.y += self.acceleration.y*dt
        delta_pos = int(self.velocity.y*dt + 0.5*(self.acceleration.y * dt**2))
        delta_pos = 1 if delta_pos == 0 else delta_pos
        self.pos.y += delta_pos  
    

        self.rect.bottom = self.pos.y
        self.drawbox.bottom = self.pos.y

    def limit_velocity(self, max_velocity, increase_vel=False):
        """
        Limits the player's velocity to a certain max
        """
        if increase_vel == True: max_velocity *= game_vars["sprint_multiplier"]
        if abs(self.velocity.x) > max_velocity:
            self.velocity.x = max_velocity if self.velocity.x > 0 else -max_velocity 
        if abs(self.velocity.x) < 0.1: self.velocity.x = 0

    def attack(self, type):
        """
        Responsible for initializing the different attacks of the player
        """
        if type == "whip_slash":
            self.append_animation("whip_slash")
        elif type == "whip_stun":
            self.append_animation("whip_stun")
        elif type == "fire_pistol":
            self.append_animation("fire_pistol")
            self.fire_bullet()

    def switch_attack(self, attack_ability):
        if attack_ability != self.current_attack_ability and not any(self.animation_state.values()):
            self.current_attack_ability = attack_ability
            switched = True
        else: switched = False
        return switched

    def fire_bullet(self):
        relative_mouse_pos = self.mouse_pos - self.rect.center
        angle = math.degrees(math.atan2(relative_mouse_pos.y, relative_mouse_pos.x))
        angle = self.limit_angle(angle)
        speed = 40
        self.global_bullets.add(Bullet(self.rect.center, angle, speed))

    def limit_angle(self, angle):
        if self.facing["left"]:
            if angle < 180 - game_vars["player_fire_angle"]/2 and angle > 0:
                return 180 - game_vars["player_fire_angle"]/2
            elif angle > -180 + game_vars["player_fire_angle"]/2 and angle < 0:
                return -180 + game_vars["player_fire_angle"]/2
            else: return angle
        elif self.facing["right"]:
            if angle > game_vars["player_fire_angle"]/2:
                return game_vars["player_fire_angle"]/2
            elif angle < -game_vars["player_fire_angle"]/2:
                return -game_vars["player_fire_angle"]/2
            else: return angle
        
    
    def handle_collisions(self, tile_collisions, axis):
        """
        Corrects the player's position if it collides with a tile
        """
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

    def create_timers(self):
        self.idle_timer = Timer("down", "ticks", 2)

        self.animation_timers = dict()
        
        rolling_animation_duration = sum(self.animator.animation_delays["rolling"])-1
        self.rolling_animation_timer = Timer("down", "ticks", rolling_animation_duration)
        self.animation_timers["rolling"] = self.rolling_animation_timer
        
        death_animation_duration = sum(self.animator.animation_delays["death"])
        self.death_animation_timer = Timer("down", "ticks", death_animation_duration)
        self.animation_timers["death"] = self.death_animation_timer

        whip_slash_duration = sum(self.animator.animation_delays["whip_slash"])
        self.whip_slash_timer = Timer("down", "ticks", whip_slash_duration)
        self.animation_timers["whip_slash"] = self.whip_slash_timer

        whip_stun_duration = sum(self.animator.animation_delays["whip_stun"])
        self.whip_stun_timer = Timer("down", "ticks", whip_stun_duration)
        self.animation_timers["whip_stun"] = self.whip_stun_timer

        fire_pistol_duration = sum(self.animator.animation_delays["fire_pistol"])
        self.fire_pistol_timer = Timer("down", "ticks", fire_pistol_duration)
        self.animation_timers["fire_pistol"] = self.fire_pistol_timer

    def find_true(self, dictionary):
        for key, value in dictionary.items():
            if value == True:
                return key
        return None