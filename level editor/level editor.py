import pygame, json, os, ctypes
import numpy as np
from spritesheet import Spritesheet

SCREENSIZE = [ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)]
SCREENSIZE[0] //= 2
SCREENSIZE[1] //= 2

MAX_X, MAX_Y = 512, 256

# placera ut spawnpoints
# när man sparar ta bort allt onödigt tomma tiles

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

def real_pos(pos, obj_height = 0):
    return (pos[0], SCREENSIZE[1] - pos[1] - obj_height)


class Tile:
    tiles = []
    def __init__(self, canvas, pos, frame, index, map):
        self.frame = frame
        self.map = map
        self.x, self.y = pos
        self.canvas = canvas
        Tile.tiles.append(self)
        self.map[int(self.y)][int(self.x)] = index + 1

    def update(self, width):
        surf = pygame.transform.scale(self.frame, (width, width))
        self.canvas.blit(surf, real_pos((self.x*width, self.y*width), width))

    def destroy(self):
        self.map[int(self.y)][int(self.x)] = 0
        Tile.tiles.remove(self)

    @classmethod
    def tile_exist(cls, x, y):
        for tile in cls.tiles:
            if (x, y) == (tile.x, tile.y):
                return True
        return False

    @classmethod
    def get_tile(cls, x, y):
        for tile in cls.tiles:
            if (x, y) == (tile.x, tile.y):
                return tile


class App:
    def __init__(self):
        
        # temp, make choise in app
        self.level, self.level_path = load_map("dev_level")
        self.frames = load_frames("dev_tiles")

        if not "map" in self.level.keys():
            self.level["map"] = np.zeros((MAX_X, MAX_Y), dtype=int).tolist()
        else:
            self.level["map"].reverse()

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

        # load tiles from save
        for y, row in enumerate(self.level["map"]):
            for x, tile in enumerate(row):
                if tile:
                    Tile(self.canvas, (x, y), self.frames[tile-1], tile-1, self.level["map"])

    def main(self):
        self.render()
        self.update()
        self.draw_lines()
        self.events()

        for tile in Tile.tiles:
            tile.update(self.tile_width)

        self.panel.update(self.canvas, self.panel_rect.x)
        
        self.display.blit(self.canvas, (0, 0))
        pygame.display.update()
        self.clock.tick(60)

    def update(self):
        self.tile_width += self.scroll
        self.scroll = 0

    def render(self):
        self.canvas.fill((0, 0, 0))
        pygame.draw.rect(self.canvas, (0, 0, 0), self.grid_rect)
        pygame.draw.rect(self.canvas, (20, 20, 20), self.panel_rect)

    def draw_lines(self):
        for i in range(int(self.grid_rect.width / self.tile_width)):
            pygame.draw.line(self.canvas, (255, 255, 255), real_pos((i*self.tile_width, 0)), real_pos((i*self.tile_width, self.grid_rect.height)))
            pygame.draw.line(self.canvas, (255, 255, 255), real_pos((0, i*self.tile_width)), real_pos((self.grid_rect.width, i*self.tile_width)))

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
                    pass
        if pygame.mouse.get_pressed()[0]:
            self.handle_tiles(pygame.mouse.get_pos())
        if pygame.mouse.get_pressed()[2]:
            self.handle_tiles(pygame.mouse.get_pos(), destroy=True)
            

    def handle_tiles(self, mouse, destroy=False):
        if not self.grid_rect.collidepoint(mouse[0], mouse[1]):
            return
        mouse = real_pos(mouse)
        x, y = (int(mouse[0] / self.tile_width)*self.tile_width, int(mouse[1] / self.tile_width)*self.tile_width)
        index = self.panel.get_selected().i
        gx, gy = x/self.tile_width, y/self.tile_width
        if not Tile.tile_exist(gx, gy) and not destroy:
            Tile(self.canvas, (gx, gy), self.frames[index], index, self.level["map"])
        elif Tile.tile_exist(gx, gy):
            Tile.get_tile(gx, gy).destroy()
        

    def save(self):
        self.level["map"].reverse()
        with open(self.level_path, "w") as file:
            json.dump(self.level, file)


class PanelTile(pygame.Surface):
    tiles = []

    def __init__(self, dim, frame, i):
        super().__init__((dim[0] + 2, dim[1] + 2))
        self.frame = frame
        self.i = i
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
        for i, frame in enumerate(frames):
            frame = pygame.transform.scale(frame, (self.tile_width, self.tile_width))
            self.frames.append(PanelTile(frame.get_size(), frame, i))
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