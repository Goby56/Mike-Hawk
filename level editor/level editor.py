import pygame, json, os, ctypes, math
import numpy as np

import tkinter as tk
from tkinter import filedialog as fd

from spritesheet import Spritesheet
from tileset import load_set

SCREENSIZE = [ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)]
SCREENSIZE[0] //= 2
SCREENSIZE[1] //= 2

MAX_X, MAX_Y = 512, 256

# bör göra om struktur på karta, [[(tile, layer), (tile, layer), (tile, layer)]]

base_dir = os.path.abspath(os.path.dirname(__file__))
asset_dir = os.path.join(base_dir, "assets")
map_dir = os.path.join(base_dir, "maps")

def try_create_file(path):
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write("{}")

def load_map(path):
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
    def __init__(self, canvas, pos, frame, index, map, layer):
        self.frame = frame
        self.map = map
        self.x, self.y = pos
        self.canvas = canvas
        Tile.tiles.append(self)
        x, y = int(self.x), int(self.y)
        self.map[y][x][0] = index + 1
        self.map[y][x][1] = layer

    def update(self, width, offset):
        surf = pygame.transform.scale(self.frame, (width, width))
        self.canvas.blit(surf, real_pos((self.x*width+offset[0], self.y*width+offset[1]), width))

    def destroy(self):
        self.map[int(self.y)][int(self.x)][0] = 0
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
        
        # open and load files
        tk.Tk().withdraw()
        level = fd.askopenfile()
        if not level: quit()
        self.level, self.level_path = load_map(level.name)

        if not "tile set" in self.level.keys():
            self.level["tile set"] = "dev_tileset"
        self.tileset = load_set(asset_dir, self.level["tile set"])

        if not "spawn" in self.level.keys():
            self.level["spawn"] = (0, 0)

        if not "map" in self.level.keys():
            self.level["map"] = []
            for rows in range(MAX_Y):
                self.level["map"].append([])
                for columns in range(MAX_X):
                    self.level["map"][rows].append([0, "fg"])
        else:
            self.level["map"].reverse()


        # pygame stuff
        self.display = pygame.display.set_mode(SCREENSIZE)
        self.canvas = pygame.Surface(SCREENSIZE)
        self.rect = self.canvas.get_rect()
        self.clock = pygame.time.Clock()

        # widgets
        panel_width = SCREENSIZE[0] // 4
        self.panel_rect = pygame.Rect((self.rect.width - panel_width, 0), (panel_width, self.rect.height))
        self.main_panel = Panel(panel_width, self.rect.height, self.tileset["fg"], "fg")
        self.bg_panel = Panel(panel_width, self.rect.height, self.tileset["bg"], "bg")

        self.panels = [self.main_panel, self.bg_panel]
        self.page = 0

        # grids
        self.tile_width = 40
        self.grid_rect = pygame.Rect((0, 0), (self.rect.width - self.panel_rect.width, self.rect.width - self.panel_rect.width))
        self.scroll = 0
        self.scroll_speed = 1
        self.x_offset, self.y_offset = 0, 0

        #load other assets
        self.spawn_surface = pygame.image.load(os.path.join(base_dir, "assets", "spawn_point.png"))

        # load tiles from save
        self.load_tiles()
        # self.load_tiles("dt")

    def load_tiles(self):
        for y, row in enumerate(self.level["map"]):
            for x, tile in enumerate(row):
                if tile[0]:
                    index = tile[0]-1
                    layer = tile[1]
                    Tile(self.canvas, (x, y), self.tileset[layer][index], 
                        index, self.level["map"], layer)

    def main(self):
        self.render()
        self.update()
        self.draw_lines()
        self.events()

        for tile in Tile.tiles:
            tile.update(self.tile_width, (self.x_offset, self.y_offset))
        
        # draws spawnpoint
        spawn_pos = real_pos((self.level["spawn"][0]*self.tile_width + self.x_offset, 
            self.level["spawn"][1]*self.tile_width + self.y_offset - self.tile_width), self.tile_width)
        surf = pygame.transform.scale(self.spawn_surface, (int(self.tile_width*1.5), int(self.tile_width*3)))
        self.canvas.blit(surf, surf.get_rect(midbottom = spawn_pos).topleft)

        self.current_panel().update(self.canvas, self.panel_rect.x)
        
        pygame.mouse.get_rel()
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
        extra_lines = math.ceil(max((abs(self.y_offset), abs(self.x_offset)))/self.tile_width)
        lines = math.ceil(self.grid_rect.width / self.tile_width)

        for i in range(lines + extra_lines):
            pygame.draw.line(self.canvas, (60, 60, 60), real_pos((i*self.tile_width + self.x_offset, 0)),
                real_pos((i*self.tile_width + self.x_offset, self.grid_rect.height)))
            pygame.draw.line(self.canvas, (60, 60, 60), real_pos((0, i*self.tile_width + self.y_offset)),
                real_pos((self.grid_rect.width, i*self.tile_width + self.y_offset)))

    def events(self):
        mouse = pygame.mouse.get_pos()
        button = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save(); quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    self.scroll = -self.scroll_speed if self.tile_width > self.scroll_speed else 0
                elif event.button == 4:
                    self.scroll = self.scroll_speed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and self.page > 0:
                    self.page -= 1
                elif event.key == pygame.K_d and self.page+1 < len(self.panels):
                    self.page += 1
        
        other_keys = [keys[pygame.K_SPACE], keys[pygame.K_LALT]]
        if button[0] and not any(other_keys):
            self.manage_tiles(mouse, mode="place")
        if button[2]:
            self.manage_tiles(mouse, mode="destroy")
        if button[0] and keys[pygame.K_LALT]:
            self.manage_tiles(mouse, mode="spawn")

        if button[0] and keys[pygame.K_SPACE]:
            rel = pygame.mouse.get_rel()
            self.x_offset += rel[0] if self.x_offset + rel[0] < 0 else 0
            self.y_offset -= rel[1] if self.y_offset - rel[1] < 0 else 0

    def current_panel(self):
        return self.panels[self.page]

    def convert_mouse(self, mouse):
        mouse = real_pos((mouse[0] - self.x_offset, mouse[1] + self.y_offset))
        x, y = (int(mouse[0] / self.tile_width)*self.tile_width, int(mouse[1] / self.tile_width)*self.tile_width)
        return x/self.tile_width, y/self.tile_width

    def manage_tiles(self, mouse, mode="place"):
        if not self.grid_rect.collidepoint(mouse[0], mouse[1]):
            return
        panel = self.current_panel()
        x, y = self.convert_mouse(mouse)
        index = panel.get_selected().index
        tile_exist = Tile.tile_exist(x, y)

        if tile_exist:
            if mode == "destroy":
                Tile.get_tile(x, y).destroy()
        else:
            if mode == "place":
                Tile(self.canvas, (x, y), panel.frames[index], index, self.level["map"], panel.layer)
            elif mode == "spawn":
                self.level["spawn"] = (x, y)

    def save(self):
        self.level["map"].reverse()
        with open(self.level_path, "w") as file:
            json.dump(self.level, file)


class PanelTile(pygame.Surface):
    def __init__(self, dim, frame, index):
        super().__init__((dim[0] + 2, dim[1] + 2))
        self.frame = frame
        self.index = index
        self.rect = self.get_rect()
        self.selected = False

    def select(self, tiles):
        for tile in tiles:
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
    def __init__(self, width, height, tiles, layer):
        self.width= width
        self.layer = layer
        self.frames = tiles

        self.padding = 10
        self.tile_width = int((self.width-4*self.padding)/3)

        self.tiles = []
        for i, tile in enumerate(tiles):
            tile = pygame.transform.scale(tile, (self.tile_width, self.tile_width))
            self.tiles.append(PanelTile(tile.get_size(), tile, i))
        self.tiles[0].selected = True

        self.canvas = pygame.Surface((width, height))

    def get_selected(self):
        for frame in self.tiles: 
            if frame.selected:
                return frame

    def update(self, canvas, x):
        self.update_tiles(x)
        canvas.blit(self.canvas, (x, 0))

    def update_tiles(self, x):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] - x, mouse_pos[1])
        clicked = pygame.mouse.get_pressed()[0]

        for i, row, column in panel_loop(len(self.tiles)):
            pos = (column*(self.tile_width+self.padding) + self.padding, 
                    row*(self.tile_width+self.padding) + self.padding)

            tile = self.tiles[i]
            tile.update(self.canvas, pos)
            if tile.rect.collidepoint(mouse_pos) and clicked:
                tile.select(self.tiles)


if __name__ == "__main__":
    app = App()
    while True:
        app.main()