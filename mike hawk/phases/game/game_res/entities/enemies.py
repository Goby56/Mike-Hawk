import pygame, sys, os, json
sys.path.append("..")

from res.config import game_vars, colors, MAX_Y, bounding_boxes, _base_dir
from phases.game.game_res.map import Tile
from res.spritesheet import Spritesheet
from res.animator import Animator
from res.timers import Timer

TILES_SIZE = game_vars["tile_size"]

class Enemy(pygame.sprite.Sprite):
    """
    An enemy class made for inheritance
    """
    def __init__(self, spawn_pos, canvas):
        super().__init__()

        x, y = spawn_pos
        pos = (x*TILES_SIZE, (MAX_Y - y)*TILES_SIZE)

        self.pos = pygame.Vector2(pos)
        self.canvas = canvas

        self.spritesheet = Spritesheet("gorilla")
        self.animator = Animator("gorilla", starting_animation="idle")
        
        # Rects
        gbox = bounding_boxes["gorilla"] # Gorilla boxes
        hitbox_wh_ratio = gbox["hitbox"].x/gbox["hitbox"].y # Drawbox width/height ratio
        height = int(game_vars["tile_size"]*gbox["height"]) 
        hitbox_dim = pygame.Vector2(height*hitbox_wh_ratio, height) # Scale image to these dimensions

        self.rect = pygame.Rect((0,0), hitbox_dim)
        self.rect.midbottom = self.pos.xy

        drawbox_scaling = gbox["drawbox"].elementwise()/gbox["hitbox"].elementwise()
        drawbox_dim = hitbox_dim.elementwise()*drawbox_scaling.elementwise()

        self.drawbox = pygame.Rect((0,0), drawbox_dim)
        self.drawbox.midbottom = self.render_pos.xy

        self.attack_range = (drawbox_dim.x-hitbox_dim.x)/2
        attackbox_dim = self.attack_range, hitbox_dim.y

        self.attackbox = pygame.Rect((0,0), attackbox_dim)
        self.attackbox.midleft = self.rect.midright

        aggrobox_dim = gbox["aggrobox"].x*game_vars["tile_size"], gbox["aggrobox"].y*game_vars["tile_size"] 
        
        self.aggrobox = pygame.Rect((0,0), aggrobox_dim)
        self.aggrobox.midbottom = self.pos.xy

        for tag in self.spritesheet.frames.keys():
            for i, frame in enumerate(self.spritesheet.frames[tag]):
                self.spritesheet.frames[tag][i] = pygame.transform.scale(frame, (int(drawbox_dim.x), int(drawbox_dim.y)))

        # Tags and states
        self.collisions = {"right":False, "left":False, "top":False, "bottom":False}
        self.state = {
            "idle":False, "walking":False, "jumping":False, "aggrovated":False,
            "attacking":False, "sleeping":False, "falling":True, "angry":False 
        }
        self.animation_state = {
            "sleeping":False, "aggrovated":False, "angry":False,
            "slam_attack":False, "jump_attack":False
        } # Animations that should play all the way through
        self.current_animation = "idle"
        self.previous_state = self.state.copy()
        self.state_history = []
        self.facing = {"left":True, "right":False}
        with open(os.path.join(_base_dir, "gorilla_animation_hierarchy.json"), "r") as f:
            self.animation_hierarchy = json.load(f)


        self.velocity = pygame.Vector2(0, 0)
        self.scroll_offset = pygame.Vector2(0, 0)
        self.health = 100
        self.speed = 3
        self.agro_distance = 20
        self.attack_cooldown = 50
        self.sleeping = False

        # Timers
        self.create_timers()


    @property
    def render_pos(self):
        return pygame.Vector2(self.pos.x, self.pos.y + game_vars["tile_size"]*3/32)

    def get_collisions(self, group):
        return pygame.sprite.spritecollide(self, group, False)

    def set_state(self, state, bool=True):
        """
        Sets all states to false, then {state} to true.
        Can set the given {state} to false if {bool}=False.
        """
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
        if not debug:
            self.previous_state = self.state.copy()

            attack_animations = ["slam_attack", "jump_attack"]
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

                    else: self.animation_timers[timer].reset()

            if any(self.animation_state.values()):   
                for animation in self.animation_state.keys():
                    if self.animation_state[animation] == True:
                        if animation in attack_animations:
                            self.set_state("attacking")
                            self.velocity.x = 0
                        else: self.set_state(animation)

            elif self.collisions["bottom"] and self.velocity.x != 0:
                self.set_state("walking")
            elif self.velocity.y < 0:
                self.set_state("jumping")
            elif self.velocity.y > game_vars["gravity"]:
                self.set_state("falling")
            else:
                self.set_state(None)

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


    def move(self):
        #self.velocity.x = 
        direction = 1 if self.facing["right"] else -1
        self.pos.x += self.speed * direction
        self.rect.centerx = self.pos.x
    
    def update(self, player, tiles, scroll):
        self.check_state()
        self.check_state(debug=True)

        if player.pos.x > self.pos.x:
            self.facing["right"] = True
            self.facing["false"] = False
        elif player.pos.x < self.pos.x:
            self.facing["right"] = False
            self.facing["false"] = True

        self.attack_timer += 1
        
        if self.aggrobox.colliderect(player.rect) and not self.rect.colliderect(player.rect) and not self.sleeping:
            self.move()

        if self.attackbox.colliderect(player.rect) and self.attack_timer > self.attack_cooldown and not self.sleeping:
            self.attack_timer = 0
            print("attack")

        self.x_collisions(self.get_collisions(tiles))
        self.vertical_movement()
        self.y_collisions(self.get_collisions(tiles))

        self.pos.x += -(scroll.x)
        self.pos.y += -(scroll.y)

        self.rect.midbottom = self.pos.xy
        self.drawbox.midbottom = self.render_pos.xy
        self.aggrobox.center = self.rect.center

        if self.facing["right"]:
            self.attackbox.midleft = self.rect.midright
        elif self.facing["left"]:
            self.attackbox.midright = self.rect.midleft

    def render(self):

        frame = self.animator.get_frame("idle")
        if self.facing["left"]:
            frame = pygame.transform.flip(frame, True, False)

        self.canvas.blit(frame, self.drawbox.topleft)

        pygame.draw.rect(self.canvas, colors["cool blue"], self.drawbox, width=1)
        pygame.draw.rect(self.canvas, colors["red"], self.rect, width=1)
        pygame.draw.rect(self.canvas, colors["green"], self.attackbox, width=1)
        pygame.draw.rect(self.canvas, colors["hot pink"], self.aggrobox, width=1)

    def vertical_movement(self):
        self.velocity.y += game_vars["gravity"]
        self.pos.y += self.velocity.y

        self.rect.bottom = self.pos.y

    def jump(self):
        """jumps"""

    def x_collisions(self, collisions):
        for tile in collisions:
            if self.velocity.x > 0:
                self.rect.right = tile.rect.left
                self.collisions["right"] = True
            elif self.velocity.x < 0:
                self.rect.left = tile.rect.right
                self.collisions["left"] = True
            self.velocity.x = 0

        self.pos.x = self.rect.centerx

        if len(collisions): return True
        return False

    def y_collisions(self, collisions):
        for tile in collisions:
            if self.velocity.y < 0:
                self.rect.top = tile.rect.bottom
                self.collisions["top"] = True
            elif self.velocity.y > 0:
                self.rect.bottom = tile.rect.top
                self.collisions["bottom"] = True
            self.velocity.y = 0
        self.pos.y = self.rect.bottom

        if len(collisions): return True
        return False

    def create_timers(self):
        self.idle_timer = Timer("down", "ticks", 2)

        self.animation_timers = dict()
        
        stand_up_duration = sum(self.animator.animation_delays["stand_up"])
        self.stand_up_timer = Timer("down", "ticks", stand_up_duration)
        self.animation_timers["rolling"] = self.stand_up_timer

        angry_animation_duration = sum(self.animator.animation_delays["angry"])
        self.stand_up_timer = Timer("down", "ticks", stand_up_duration)
        self.animation_timers["rolling"] = self.stand_up_timer

        self.attack_timer = 0

    def find_true(self, dictionary):
        for key, value in dictionary.items():
            if value == True:
                return key
        return None

    def sleep(self):
        """
        called when hit by bullet
        """
        self.sleeping = True

    def knockback(self):
        """
        called when hit with knockback attack
        """
        self.velocity[0] += self.direction*3
        self.velocity[1] -= 2
        # ändra bild

    def anger(self): # stå på bakbenen och slå på bröstet (står stilla så man hinner fly och hämta mer ammo)
        """
        called when hit with stun attack
        """
        

