from io import SEEK_CUR
import pygame
from .config import SCREENSIZE, SCREEN_WIDTH, SCREEN_HEIGHT, menubutton, colors, screen_scale_x, screen_scale_y

def blurSurf(surface, amt):
    """
    Blur the given surface by the given 'amount'.  Only values 1 and greater
    are valid.  Value 1 = no blur.
    """
    if amt < 1.0:
        raise ValueError("Arg 'amt' must be greater than 1.0, passed in value is %s"%amt)
    scale = 1.0/float(amt)
    surf_size = surface.get_size()
    scale_size = (int(surf_size[0]*scale), int(surf_size[1]*scale))
    surf = pygame.transform.smoothscale(surface, scale_size)
    surf = pygame.transform.smoothscale(surf, surf_size)
    return surf

class BackgroundParalax:
    def __init__(self, canvas, layers):
        self.layers = [[image, [0,0]] for image in layers]
        for i, layer in enumerate(self.layers):
            self.layers[i][0] = pygame.transform.scale(layer[0], canvas.get_size())
        self.canvas = canvas
        self.total_scroll_x = 0
    
    def update(self, scroll):
        self.total_scroll_x += scroll
        for i in range(len(self.layers)-1):
            layer_offset = -self.total_scroll_x*(i+1)**2/50
            index = -layer_offset//self.canvas.get_width()
            self.layers[1:][i][1][0] = layer_offset 
            self.layers[1:][i][1][0] += index*self.canvas.get_width()
        
    def render(self, game_canvas):
        self.menu_canvas = game_canvas
        for layer in self.layers:
            x = layer[1][0]
            y = layer[1][1]
            self.canvas.blit(layer[0], (x, y))
            self.canvas.blit(layer[0], (x+self.canvas.get_width(), y))
            self.canvas.blit(layer[0], (x-self.canvas.get_width(), y))
        self.canvas.blit(blurSurf(self.menu_canvas, 1), (0,0))

class MenuButton:
    rect = menubutton.get_rect()
    def __init__(self, surface, listener, pos, text, command=None, scale_x=2, scale_y=3, font_size=1):
        self._surface = surface
        self.orig_rect = menubutton.get_rect()
        self._image = menubutton.copy()
        self._command = command
        self._text = text
        self._listener = listener
        self.scale_x = screen_scale_x*scale_x
        self.scale_y = screen_scale_y*scale_y
        self.font_size = int(60 * screen_scale_y * font_size)

        self._image = pygame.transform.scale(self._image, (int(self.scale_x*self.orig_rect.width), int(self.scale_y*self.orig_rect.height)))

        font = pygame.font.SysFont("Ariel", self.font_size)
        font_surf = font.render(self._text, True, colors["white knight"])
        img_center, font_center = self._image.get_rect().center, font_surf.get_rect().center
        center = (img_center[0] - font_center[0], img_center[1] - font_center[1])

        self._image.blit(font_surf, center)
        self.rect = pygame.Rect(pos, self._image.get_size())

    def update(self):
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            surf = pygame.transform.scale(self._image, 
                    (int(self.rect.width*1.2), int(self.rect.height*1.2)))
            self._listener.on_click(1, self._command)
        else:
            surf = self._image

        rect = surf.get_rect()
        topleft = (self.rect.left - (rect.width-self.rect.width)//2, 
                self.rect.top - (rect.height - self.rect.height)//2)

        self._surface.blit(surf, topleft)


class MenuButtonPanel:
    def __init__(self, surface, listener, start_pos, buttons: int, padding, texts: list, commands: list, scl_x=4, scl_y=3):
        self._surface = surface
        self._listener = listener
        self.pos = start_pos
        self.buttons = []
        self.padding = padding * screen_scale_y
        for i in range(buttons):
            self.buttons.append(MenuButton(surface, listener, (start_pos[0], start_pos[1]+(MenuButton.rect.height+self.padding)*i),
                texts[i], command=commands[i], scale_x=scl_x, scale_y=scl_y))

    def update(self):
        for button in self.buttons:
            button.update()


class ToolButton:
    def __init__(self, canvas, listener, pos, size, image):
        self._canvas, self._listener = canvas, listener
        self.x, self.y = pos
        self.size = size
        self._image = pygame.transform.scale(image, (size, size))
        self._binding = False
        self.rect = pygame.Rect(pos, (size, size))
        self.selected = False

    def update(self, mouse):
        if ((self.rect.collidepoint(mouse[0], mouse[1]) and self._listener.mouse_clicked(1))
        or (self._binding and self._listener.key_pressed(self._binding))):
            self.selected = True
            return True
        self._canvas.blit(self._image, (self.x, self.y))
        if self.selected:
            pygame.draw.rect(self._canvas, colors["white knight"], (self.x, self.y, self.size, self.size), 3)
        self.rect.topleft = (self.x, self.y)

    def bind(self, key):
        self._binding = key
            

class Toolbar:
    def __init__(self, canvas, listener, pos, images, padding):
        self._canvas, self._listener = canvas, listener
        self._buttons = []
        self._mouse = (0, 0)
        
        btn_size = SCREENSIZE[1] // 20
        
        self.dim = (len(images)*(padding+btn_size)+padding, 
            2*padding + btn_size)
        self.pos = pos
        self.rect = pygame.Rect(pos, self.dim)

        self._surface = pygame.Surface(self.dim)
        self._surface.fill(colors["black magic"])

        for i, image in enumerate(images):
            self._buttons.append(ToolButton(self._canvas, self._listener,
                (i*btn_size+(i+1)*padding+self.pos[0], padding+self.pos[1]), btn_size, image))
        self.selected = self._buttons[0]
        self._buttons[0].selected = True
        
    def update(self):
        self._mouse = pygame.mouse.get_pos()
        self._canvas.blit(self._surface, self.pos)
        for button in self._buttons:
            if button.selected:
                self.selected = button
            if button.update(self._mouse) and button != self.selected:
                self.selected.selected = False

    def hover(self):
        if self.rect.collidepoint(self._mouse):
            return True
        return False

    def get_selected(self):
        return self._buttons.index(self.selected)

    def bind(self, *args):
        """args: (key, index)"""
        for key, index in args:
            self._buttons[index].bind(key)

if __name__ == "__main__":
    pygame.font.init()