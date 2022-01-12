import pygame, sys
sys.path.append("..")

from res.config import game_vars, MAX_Y


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