import pygame, os, json

from main import State, Main

class Game(State):
    def __init__(self, game):
        self.game = game
        State.__init__(self, game)
        tile_map_path = os.path.join(self.game.assets_directory, "tile_map.json")
        with open(tile_map_path) as f:
            self.tile_map = json.load(f)
        self.tiles = self.place_tiles(self.tile_map)
        self.player = Player(self.game, self)

    def update(self, dt, inputs):
        self.player.update(dt, inputs)

    def render(self, surface):
        surface.fill((200,200,200))
        self.tiles.draw(self.game.screen)
        self.player.render(self.game.screen)

    def place_tiles(self, tile_map):
        tile_group = pygame.sprite.Group()
        for r in range(len(tile_map["map"])):
            for c in range(len(tile_map["map"][r])):
                if tile_map["map"][r][c] == 1:
                    tile_group.add(Tile(self.game, (int(c),int(r))))
        return tile_group


class Tile(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        super().__init__()
        self.game = game
        self.pos = pos[0]*72, pos[1]*72
        image_path = os.path.join(self.game.assets_directory, "24x24_block.png")
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (72,72))
        self.rect = self.image.get_rect(topleft = self.pos)

class Player(pygame.sprite.Sprite):
    def __init__(self, game, state):
        super().__init__()
        self.game = game
        self.state = state
        self.pos = pygame.Vector2(4*72, 6*72)
        image_path = os.path.join(self.game.assets_directory, "slime.png")
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (44,20))
        self.rect = self.image.get_rect(midbottom = (self.pos.x, self.pos.y))

        self.gravity, self.friction = 0.5, -0.2
        self.acceleration = pygame.Vector2(0,self.gravity)
        self.velocity = pygame.Vector2(0,0)

        self.onground = False
        self.collisions = {"right":False, "left":False, "top":False, "bottom":False}

    def update(self, dt, inputs):
        self.horizontal_movement(dt, inputs)
        self.handle_collisions(self.get_collisions(self.rect, self.state.tiles), axis=0)

        self.vertical_movement(dt, inputs) 
        self.handle_collisions(self.get_collisions(self.rect, self.state.tiles), axis=1)

    def get_collisions(self, rect, group):
        collision_list = []
        for sprite in group:
            if rect.colliderect(sprite.rect):
                collision_list.append(sprite)
        return collision_list

    def handle_collisions(self, collision_list, axis):
        for collision in self.collisions:
            self.collisions[collision] = False

        if len(collision_list) > 0:
            if axis == 0:
                for tile in collision_list:
                    if self.velocity.x > 0:
                        self.rect.right = tile.rect.left
                        self.collisions["right"] = True
                    elif self.velocity.x < 0:
                        self.rect.left = tile.rect.right
                        self.collisions["left"] = True
            
            elif axis == 1:
                for tile in collision_list:
                    if self.velocity.y > 0:
                        self.rect.bottom = tile.rect.top
                        self.collisions["bottom"] = True
                        self.onground = True
                        self.velocity.y = 0
                    elif self.velocity.y < 0:
                        self.rect.top = tile.rect.bottom
                        self.collisions["top"] = True

            self.pos.xy = self.rect.topleft

    def horizontal_movement(self, dt, inputs):
        dt *= 60

        direction = inputs["d"] - inputs["a"]
        self.acceleration.x = 2*direction
        
        self.velocity.x += self.acceleration.x + self.velocity.x*self.friction
        self.limit_velocity(10)
        self.pos.x += self.velocity.x * dt

        self.rect.x = self.pos.x

    def vertical_movement(self, dt, inputs):
        dt *= 60

        if inputs["space"]:
            self.jump()

        self.onground = False

        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > 15: self.velocity.y = 15
        self.pos.y += self.velocity.y*dt + 0.5*(self.acceleration.y * dt**2)
        
        self.rect.y = self.pos.y

    def jump(self):
        if self.onground:
            self.jumping = True
            self.velocity.y = -10
            self.onground = False

    def render(self, surface):
        surface.blit(self.image, (self.pos.x, self.pos.y))

    def limit_velocity(self, max_velocity):
        if abs(self.velocity.x) > max_velocity:
            self.velocity.x = max_velocity if self.velocity.x > 0 else -max_velocity 
        #self.velocity.x = min(-max_velocity, max(self.velocity.x, max_velocity))
        if abs(self.velocity.x) < 0.1: self.velocity.x = 0


# collision_list = self.collisions(self.rect, self.state.tiles)
#         if len(collision_list) > 0:
#             for tile in collision_list:
#                 if self.velocity.x > 0:
#                     self.rect.right = tile.rect.left
#                     self.pos.x = self.rect.x
                    
#                 elif self.velocity.x < 0:
#                     self.rect.left = tile.rect.right
#                     self.pos.x = self.rect.x
#         else:
#             self.acceleration.x = 0
#             if inputs["d"]:
#                 self.acceleration.x = 1
#             elif inputs["a"]:
#                 self.acceleration.x = -1

#             self.acceleration.x += self.velocity.x * self.friction * dt
#             self.velocity.x += self.acceleration.x * dt
#             self.limit_velocity(8)
#             self.pos.x += self.velocity.x*dt + 0.5*(self.acceleration.x * dt**2)