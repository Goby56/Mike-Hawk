import pygame, json, ctypes, os, math

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog as sd

from res.tileset import load_set
from res.widgets import MenuButtonPanel, Toolbar, MenuButton
from phases.phase import Phase
from res.config import colors, _base_dir, paralax_layers, editor_buttons
from listener import Listener


SCREENSIZE = [ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)]
SCREENSIZE[0] //= 2
SCREENSIZE[1] //= 2

MAX_X, MAX_Y = 1024, 256 # flytta till config
SETDIR = os.path.join(_base_dir, "assets", "tilesets")
pygame.font.init()

# add scroll in tile panel
# fix bugs
# new trigger system. trigger register: name: type, command. triggers: {pos: pos, name: name}
# add slopes and entities and spawn and details

def load_level(path):
    with open(path, "r") as file:
        json_dict = json.load(file)
    return json_dict


class Menu(Phase):
    def __init__(self, canvas, listener):
        self.canvas = canvas
        self.listener = listener
        self.btn_panel = MenuButtonPanel(
            self.canvas, listener, (10, 10), 3, 10, 
            ["New Map", "Load Map", "Quit"], 
            [self.new_map, self.load_map, quit]
        )
        tk.Tk().withdraw()

    def update(self):
        self.canvas.fill(colors["white knight"])
        self.btn_panel.update()

    def create_file(self, path, tileset):
        with open(path, "w") as file:
            level = {}
            level["tileset"] = tileset.split(".")[0]
            level["spawn"] = (0, MAX_Y)
            level["details"] = []
            level["entities"] = []
            level["map"] = {}
            level["triggers"] = []
            json.dump(level, file)

    def new_map(self):
        tilepath = fd.askopenfilename(
            initialdir=os.path.join(_base_dir, "assets", "tilesets"),
            defaultextension='.json', 
            filetypes=[("tilesets,", '*.png')]
        )
        if not tilepath: quit()
        tileset = os.path.split(tilepath)[1]
        level = fd.asksaveasfilename(defaultextension='.json', 
            filetypes=[("level files, ", '*.json')], 
            initialdir=os.path.join(_base_dir, "levels"))
        if not level: quit()
        self.create_file(level, tileset)
        Phase.enter_phase(Editor(self.canvas, 
            self.listener, level))

    def load_map(self):
        level = fd.askopenfilename(defaultextension='.json', 
            filetypes=[("level files, ", '*.json')], 
            initialdir=os.path.join(_base_dir, "levels"))
        Phase.enter_phase(Editor(self.canvas, 
            self.listener, level))

class Editor(Phase):
    def __init__(self, canvas, listener, path):
        self.canvas = canvas
        self.listener = listener
        self.path = path
        with open(self.path, "r") as file:
            global level 
            level = json.load(file)
        
        # tile things
        tileset = load_set(SETDIR, level["tileset"])
        self.tileset = [list(tileset["fg"]), list(tileset["bg"])]

        self.tile = 50
        self.tiles = []

        self.triggers = []

        self.load_data()

        self.layer = 0

        #movement
        self.x_offset = 0
        self.y_offset = 0

        # inputs
        self.modes = ["place", "delete", "select", "entity", "spawn"]
        self.mode = "place"

        tmp = pygame.Surface((20, 20))
        tmp.fill(colors["red"])
        pen, eraser, marker, entity, layer1, layer2 = editor_buttons
        self.toolbar = Toolbar(self.canvas, self.listener, (70, 0), 
            [pen, eraser, marker, entity, tmp], 5)
        self.toolbar.bind(("b", 0), ("e", 1), ("m", 2))
        
        self.layer_panel = Toolbar(self.canvas, self.listener, (self.toolbar.pos[0] + self.toolbar.dim[0] + 10, 0), 
            [layer1, layer2], 5)
        self.layer_panel.bind(("1", 0), ("2", 1))

        self.panel = Panel(self.canvas, SCREENSIZE[0] // 8, self.tileset)
        
        #backgtound
        self.paralax_layers = [pygame.transform.scale(layer, SCREENSIZE) for layer in paralax_layers]

        #functions
        self.func_keys = {"space": False}
        self.hold = False
        self.selection = None
        self.other = False

    @property
    def mouse(self):
        mouse = pygame.mouse.get_pos()
        x_pos, y_pos = mouse[0]-self.x_offset, SCREENSIZE[1] - mouse[1]+self.y_offset
        return x_pos//self.tile, MAX_Y - y_pos//self.tile - 1

    def update(self):
        for layer in self.paralax_layers:
            self.canvas.blit(layer, (0, 0))

        self.mode = self.modes[self.toolbar.get_selected()]
        self.layer = self.layer_panel.get_selected()

        if any(self.func_keys.values()) or any([self.toolbar.hover(), self.layer_panel.hover(), self.panel.hover() and self.mode == "place"]): 
            self.other = True
        else:
            self.other = False

        for key in self.func_keys.keys():
            self.func_keys[key] = self.listener.key_pressed(key, hold=True)
        self.listener.on_key("escape", self.exit)
        self.listener.on_event("quit", self.exit)
        
        self.get_movement()

        if self.listener.mouse_clicked(1, hold=True) and self.mode in ["place", "delete", "spawn", "entity"] and not self.other:
                exec("self.{}()".format(self.mode))

        if self.mode == "select": self.select()
        else: self.selection = None
        if self.listener.key_pressed("m"): self.selection = None

        for tile in self.tiles:
            layer = self.layer if self.mode in ["place", "delete", "select"] else 2
            tile.update(self.tile, self.x_offset, self.y_offset, layer)

        for trigger in self.triggers:
            trigger.render(self.canvas, self.tile, 
                self.x_offset, self.y_offset
            )

        if self.listener.key_pressed("left control", hold=True) and self.listener.key_pressed("s"):
            self.save()

        self.draw_lines()
        self.toolbar.update()
        self.layer_panel.update()

        if self.mode == "place":
            self.panel.update(self.layer)
            way = 0
            if self.listener.key_pressed("d"): way = 1
            elif self.listener.key_pressed("a"): way = -1
            elif self.listener.key_pressed("w"): way = -3
            elif self.listener.key_pressed("s"): way = 3
            self.panel.next_tile(self.layer, way)
            
        if self.selection != None:
            self.selection.render(self.canvas, self.tile, self.x_offset, self.y_offset)
        
        pygame.mouse.get_rel()
        self.update_level()
        
    def update_level(self):
        level["map"] = {"{}, {}".format(tile.x, tile.y): (tile.index, tile.layer) for tile in self.tiles}
        level["triggers"] = [trigger.dict for trigger in self.triggers]

    def load_data(self):
        for tile in level["map"]:
            x, y = tile.split(", ")
            layer = level["map"][tile]
            self.new_tile(int(x), int(y), layer[0], layer[1])
        
        for trigger in level["triggers"].copy():
            self.new_trigger(trigger["pos"], trigger["name"])

    def new_tile(self, x, y, index, layer):
        image = self.tileset[layer][index]
        self.tiles.append(Tile(self.canvas, (x, y), layer, image, index))

    def get_tile(self, x, y):
        for tile in self.tiles:
            if (tile.x, tile.y) == (x, y):
                return tile
        return False

    def new_trigger(self, pos, name):
        self.triggers.append(Trigger(pos, name))

    def add_trigger(self, name, command, type):
        level["register"][name] = [command, type]

    def remove_trigger(self, name):
        del level["register"][name]

    def get_movement(self):
        if self.listener.mouse_clicked(4): self.tile -= 1
        if self.listener.mouse_clicked(5): self.tile += 1

        if self.func_keys["space"] and self.listener.mouse_clicked(1, hold=True):
            rel = pygame.mouse.get_rel()
            self.x_offset += rel[0] if self.x_offset + rel[0] < 0 else 0
            self.y_offset += rel[1] if self.y_offset + rel[1] > 0 else 0

    def place(self):
        x, y = self.mouse
        tile = self.get_tile(x, y)
        index = 0
        if tile and (tile.layer != self.layer or tile.image == self.tileset[self.layer][index]):
            return
        self.new_tile(x, y, self.panel.get_selected(self.layer), self.layer)

    def delete(self):
        tile = self.get_tile(*self.mouse)
        if tile and tile.layer == self.layer:
            self.tiles.remove(tile)

    def spawn(self):
        x, y = self.mouse
        print("spawn set at:", x, y)
        level["spawn"] = [x, y]

    def entity(self):
        pass

    def select(self):
        if self.listener.mouse_clicked(1, hold=True):
            if self.listener.key_pressed("left control", hold=True):
                if self.hold == True and self.selection == None:
                    self.selection = Selection(self.mouse, self.tile)
                if self.selection != None:
                    if self.hold == False: self.selection.new_selection(self.mouse)
                    self.selection.get_endpos(self.mouse, self.tiles, self.layer)
                self.hold = True
            else: self.hold = False
            if self.selection != None and self.hold == False and not self.other:
                self.selection.move(self.mouse)


    def draw_lines(self):
        for x in range(int(SCREENSIZE[0]//self.tile) + 1):
            pygame.draw.line(self.canvas, colors["black magic"], 
                (x*self.tile + self.x_offset % self.tile, 0), 
                (x*self.tile + self.x_offset % self.tile, SCREENSIZE[1]))
        for y in range(int(SCREENSIZE[1]//self.tile) + 1):
            pygame.draw.line(self.canvas, colors["black magic"], 
                (0, SCREENSIZE[1] - y*self.tile + self.y_offset % self.tile), (SCREENSIZE[0], 
                SCREENSIZE[1] - y*self.tile + self.y_offset % self.tile))

    def save(self):
        print("Saving...")
        with open(self.path, "w") as file:
            json.dump(level, file, indent=4)

    def exit(self):
        if mb.askyesno("Save?", "Do you want to save?"):
            self.save()
        quit()


class App:
    def __init__(self):
        self._display = pygame.display.set_mode(SCREENSIZE)
        self._clock = pygame.time.Clock()

        self.canvas = pygame.Surface(SCREENSIZE)
        self.listerner = Listener()
        Phase.enter_phase(Menu(self.canvas, self.listerner))

    def main(self):
        self.canvas.fill(colors["white knight"])
        self.listerner.listen()

        phase = Phase.get_current()
        phase.update()
        phase.render()

        self.listerner.on_event("quit", quit)

        self._display.blit(self.canvas, (0, 0))
        pygame.display.update()
        self._clock.tick(60)


class Tile:
    def __init__(self, canvas, pos, layer, image, index):
        self.canvas = canvas
        self.x, self.y = pos
        self.image = image
        self.layer = layer
        self.index = index
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def update(self, dim, x_offset, y_offset, layer=0, panel=False):
        dim = int(dim)
        surf = pygame.transform.scale(self.image, (dim,dim))
        self.rect = surf.get_rect()
        self.rect.topleft = (self.x, self.y)

        if panel:
            self.canvas.blit(surf, (self.x, self.y))
        else:    
            self.canvas.blit(surf, (self.x*dim+x_offset, SCREENSIZE[1]-(MAX_Y-self.y)*dim+y_offset))
        if self.layer != layer and layer <= 1:
            pygame.draw.rect(self.canvas, colors["white knight"], 
                (self.x*dim+x_offset, SCREENSIZE[1]-(MAX_Y-self.y)*dim+y_offset, dim, dim), 2)


class Trigger:
    """
    type
    0: can be triggerd only once
    1: can be triggerd mutible times but must exit zone
    2: alwas triggerd if player inside
    """
    def __init__(self, pos, name):
        self.x, self.y = pos
        self.surface = pygame.Surface((1, 1)) # temp, make image
        self.surface.fill(colors["blue"])
        self.surface.set_alpha(100)

        self.dict = {
            "pos": pos,
            "name": name
        }
        
    def render(self, canvas, dim, x_offset, y_offset):
        dim = int(dim)
        surf = pygame.transform.scale(self.surface, (dim, dim))
        canvas.blit(surf, (self.x*dim+x_offset, SCREENSIZE[1]-(MAX_Y-self.y)*dim+y_offset, dim, dim))


class Selection:
    def __init__(self, mouse, size):
        self.start_pos = mouse
        self.tiles = []

        # visual, only for making selection box
        self.rect = pygame.Rect((0, 0), (size, size))

    def new_selection(self, pos):
        self.start_pos = pos
        self.tiles = []

    def get_tiles(self, tiles, layer):
        x1, y1 = self.start_pos
        x2, y2 = self.end_pos
        for tile in tiles:
            if (tile.x >= x1 and tile.x <= x2
            and tile.y >= y1 and tile.y <= y2
            and tile not in self.tiles
            and tile.layer == layer):
                self.tiles.append(tile)

    def get_endpos(self, mouse, tiles, layer):
        self.end_pos = (mouse[0], mouse[1])
        self.get_tiles(tiles, layer)
       
    def render(self, surface, size, x_offset, y_offset):
        x1, y1 = self.start_pos
        x2, y2 = self.end_pos
        self.rect.x = x1*size+x_offset
        self.rect.y = SCREENSIZE[1]-(MAX_Y-y1)*size+y_offset
        self.rect.size = ((x2+1-x1)*size, (y2+1-y1)*size)

        pygame.draw.rect(surface, colors["white knight"], self.rect, 3)

    def move(self, mouse):
        x, y = self.start_pos
        relx = mouse[0] - x
        rely = mouse[1] - y
        for tile in self.tiles:
            tile.x += relx
            tile.y += rely
        self.start_pos = (self.start_pos[0] + relx, self.start_pos[1] + rely)
        self.end_pos = (self.end_pos[0] + relx, self.end_pos[1] + rely)


def set_tiles(surface, images, layer, size, padding):
    lst = []
    i = 0
    for y in range(len(images) // 3 + 1):
        for x in range(3):
            pos = (x*(size+padding) + padding, y*(size+padding) + padding)
            if i < len(images):
                lst.append(Tile(surface, pos, layer, images[i], i))
            i += 1
    return lst


class Panel:
    def __init__(self, canvas, width, tileset):
        self.canvas = canvas
        self.surface = pygame.Surface((width, SCREENSIZE[1]))
        self.width = width
        self.tileset = tileset
        self.rect = pygame.Rect(SCREENSIZE[0]-self.width, 0, self.width, SCREENSIZE[1])
        padding = 10
        self.size = SCREENSIZE[1] // 20
        template = lambda i :set_tiles(self.surface, self.tileset[i], i, self.size, padding)
        self.tiles = [template(0), template(1)]
        self.selected = self.tiles[0][0]
        self.preview_surf = pygame.Surface((width, width))
        self.preview_tile = Tile(self.preview_surf, (10, 10), 0, self.tiles[0][0].image, 0)

    def hover(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(*mouse): return True
        return False

    def get_selected(self, layer):
        return self.tiles[layer].index(self.selected)

    def next_tile(self, layer, way):
        i = (self.get_selected(layer) + way) % len(self.tiles[layer])
        self.selected = self.tiles[layer][i]

    def update(self, layer):
        self.surface.fill(colors["black magic"])
        if not self.selected in self.tiles[layer]:
            self.selected = self.tiles[layer][0]
        for tile in self.tiles[layer]:
            tile.update(self.size, 0, 0, layer, panel=True)
            x, y = pygame.mouse.get_pos()
            if tile.rect.collidepoint(x - self.rect.x, y - self.rect.y) and pygame.mouse.get_pressed()[0]:
                self.selected = tile
        pygame.draw.rect(self.surface, colors["white knight"], self.selected.rect, 3)

        self.preview_surf.fill(colors["black magic"])
        self.preview_tile.image = self.selected.image
        self.preview_tile.update(self.width-20, 0, 0, panel=True)

        self.canvas.blit(self.surface, self.rect.topleft)
        self.canvas.blit(self.preview_surf, (self.rect.x, SCREENSIZE[1]-self.width))


class Listbox:
    def __init__(self, canvas, listener, width, items):
        self.canvas = canvas
        self.width = width
        self.items = ["spawn_point"] + items # Listbox items
        self.listener = listener

        self.padding = 5
        self.selected = "spawn_point"

        self.surface = pygame.Surface((width, SCREENSIZE[1]))
        self.surface.fill(colors["black magic"])
        self.rect = self.surface.get_rect(topleft = (SCREENSIZE[0]-self.width, 0))

        self.add_button = MenuButton(self.surface, self.listener, (self.padding, SCREENSIZE[1]-50), 
            "Add Trigger", self.add_trigger
        )
        self.add_button.rect.top = SCREENSIZE[1] - self.rect.height - self.padding
        self.remove_button = MenuButton(self.surface, self.listener, (self.padding*2 + self.add_button.rect.width, 
            SCREENSIZE[1]-50), "Add Trigger", self.remove_trigger
        )

    def add_trigger(self):
        trigger = TriggerConfig()
        if trigger != None:
            name, command, type = trigger.result
            level["register"][name] = [command, type]
            self.items.append(name)

    def remove_trigger(self):
        if self.selected != "spawn_point":
            del level["register"][self.selected]
            self.items.remove(self.selected)


class ListboxItem:
    def __init__(self, canvas, pos, width, name):
        self.canvas = canvas
        self.pos = pos
        self.width = width
        self.name = name

        self.selected = False

        padding = 3
        font = pygame.font.SysFont("Ariel", 20)
        font_surf = font.render(self.name, False, colors["black magic"])
        self.surface = pygame.Surface((width, font_surf.get_height() + 2*padding))
        self.surface.fill(colors["white knight"])
        self.surface.blit(font_surf, self.pos)

    def clicked(self):
        pass # if clicked return True

    def update(self):
        pass


class TriggerConfig(sd.Dialog):
    def __init__(self):
        super().__init__(None, "New Trigger")

    def body(self, master): # function in sd.Dialog to override
        self.objects = ["name", "command", "type"]
        for i, text in enumerate(self.objects):
            tk.Label(master, text = text.capitalize() + " :").grid(row=i, column=0)
            if i < len(self.objects) - 1:
                vars(self)[text] = tk.Entry(master)
                vars(self)[text].grid(row = i, column=1)
        self.type = tk.Spinbox(master, from_ = 0, to = 2)
        self.type.grid(row = i, column=1)

        return self.name # initial focus

    def apply(self): # function in sd.Dialog to override
        self.result = [vars(self)[text].get() for text in self.objects]
    

if __name__ == "__main__":
    app = App()
    while True:
        app.main()
