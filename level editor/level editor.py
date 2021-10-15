from sys import platform
import pygame, json, os, ctypes
from spritesheet import Spritesheet

SCREENSIZE = [ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)]
SCREENSIZE[0] //= 2
SCREENSIZE[1] //= 2

base_dir = os.path.abspath(os.path.dirname(__file__))
map_dir = os.path.join(base_dir, "maps")

def try_create_file(path):
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write("{}")

def load_map(filename):
    path = os.path.join(map_dir, f"{filename}.json")
    try_create_file(path)
    with open(path, "r") as file:
        json_dict = json.load(file)
    return json_dict, path

def load_frames(filename):
    spritesheet = Spritesheet(filename) # Create object of file path
    data = spritesheet.parse_sprite() # Get meta data from sheet
    frames = spritesheet.get_frames(data) # Get sequence of frames
    return frames


class Tile:
    tiles = []
    def __init__(self, canvas, rect, tile):
        self.surf = tile.frame
        self.rect = rect
        self.canvas = canvas

    def update(self):
        self.canvas.blit(self.surf, self.rect.topleft)


class App:
    def __init__(self):
        
        # temp, make choise in app
        self.map, self.map_path = load_map("dev_level")
        self.frames = load_frames("dev_tiles")

        # pygame stuff
        self.display = pygame.display.set_mode(SCREENSIZE)
        self.canvas = pygame.Surface(SCREENSIZE)
        self.rect = self.canvas.get_rect()
        self.clock = pygame.time.Clock()

        # widgets
        panel_width = 200
        self.panel_rect = pygame.Rect((self.rect.width - panel_width, 0), (panel_width, self.rect.height))
        self.panel = Panel(panel_width, self.rect.height, self.frames)

        # grids
        self.tile_width = 40
        self.grid_rect = pygame.Rect((0, 0), (self.rect.width - self.panel_rect.width, self.rect.width - self.panel_rect.width))
        self.scroll = 0
        self.scroll_speed = 1


    @property
    def gridsize(self):
        return int(self.grid_rect.width / self.tile_width)

    def main(self):
        self.render()
        self.update()
        self.events()
        self.draw_lines()
        
        self.display.blit(self.canvas, (0, 0))
        pygame.display.update()
        self.clock.tick(60)

    def update(self):
        self.tile_width += self.scroll
        self.scroll = 0
        self.panel.update(self.canvas, self.panel_rect.x)
        for tile in Tile.tiles:
            tile.update()

    def render(self):
        self.canvas.fill((0, 0, 0))
        pygame.draw.rect(self.canvas, (0, 0, 0), self.grid_rect)
        pygame.draw.rect(self.canvas, (20, 20, 20), self.panel_rect)

    def draw_lines(self):
        for i in range(self.gridsize):
            pygame.draw.line(self.canvas, (255, 255, 255), (i*self.tile_width, 0), (i*self.tile_width, self.grid_rect.height))
            pygame.draw.line(self.canvas, (255, 255, 255), (0, i*self.tile_width), (self.grid_rect.width, i*self.tile_width))

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    self.scroll = -self.scroll_speed if self.tile_width > self.scroll_speed else 0
                elif event.button == 4:
                    self.scroll = self.scroll_speed
                elif event.button == 1:
                    self.place_tile(pygame.mouse.get_pos())

    def place_tile(self, mouse):
        x, y = int(mouse[0] / self.tile_width)*self.tile_width, int(mouse[1] / self.tile_width)*self.tile_width
        tile = self.panel.get_selected()
        pygame.draw.rect(self.canvas, (255, 0, 0), (x, y, self.tile_width, self.tile_width))
        if self.grid_rect.collidepoint(x, y):
            Tile(self.canvas, pygame.Rect((x,y), (tile.frame.get_size())), tile)

    def save(self):
        with open(self.map_path, "w") as file:
            json.dump(self.map, file)


class PanelTile(pygame.Surface):
    tiles = []

    def __init__(self, dim, frame):
        super().__init__((dim[0] + 2, dim[1] + 2))
        self.frame = frame
        self.rect = self.get_rect()
        self.selected = False
        PanelTile.tiles.append(self)

    @classmethod
    def get_selected(cls):
        for tile in cls.tiles:
            if tile.selected:
                return tile

    def select(self):
        for tile in PanelTile.tiles:
            tile.selected = False
        self.selected = True

    def update(self, canvas, pos):
        self.rect.topleft = pos
        self.fill((20, 20, 20))
        self.blit(self.frame, (1, 1))
        if self.selected:
            pygame.draw.rect(self, (255, 255, 255), ((0, 0), (self.rect.size)), 1)

        canvas.blit(self, pos)


def panel_loop(num_frames):
    i = 0
    for row in range(num_frames // 3 + 1):
        for column in range(3):
            if num_frames > i:
               yield i, row, column
            i += 1
                 

class Panel:
    def __init__(self, width, height, frames):
        self.width= width

        self.padding = 10
        self.tile_width = int((self.width-4*self.padding)/3)

        self.frames = []
        for frame in frames:
            frame = pygame.transform.scale(frame, (self.tile_width, self.tile_width))
            self.frames.append(PanelTile(frame.get_size(), frame))
        self.frames[0].selected = True

        self.canvas = pygame.Surface((width, height))

    def get_selected(self):
        return PanelTile.get_selected()

    def update(self, canvas, x):
        self.update_tiles(x)
        canvas.blit(self.canvas, (x, 0))

    def update_tiles(self, x):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] - x, mouse_pos[1])
        clicked = pygame.mouse.get_pressed()[0]

        for i, row, column in panel_loop(len(self.frames)):
            pos = (column*(self.tile_width+self.padding) + self.padding, 
                    row*(self.tile_width+self.padding) + self.padding)

            frame = self.frames[i]
            frame.update(self.canvas, pos)
            if frame.rect.collidepoint(mouse_pos) and clicked:
                frame.select()


if __name__ == "__main__":
    app = App()
    while True:
        app.main()