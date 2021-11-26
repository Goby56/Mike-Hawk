from typing import List
import pygame, json, ctypes, os

import tkinter as tk
from tkinter import filedialog as fd

from res.tileset import load_set
from res.widgets import MenuButtonPanel
from phases.phase import Phase
from res.config import colors, _base_dir
from listener import Listener


SCREENSIZE = [ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)]
SCREENSIZE[0] //= 2
SCREENSIZE[1] //= 2

MAX_X, MAX_Y = 1024, 256 # flytta till config
SETDIR = os.path.join(_base_dir, "assets", "tilesets")
pygame.font.init()

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
            level["map"] = [[(0, 0) for _ in range(MAX_X)] for _ in range(MAX_Y)]
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
            self.level = json.load(file)
        tileset = load_set(SETDIR, self.level["tileset"])
        self.tileset = [layer for layer in tileset[:2]]

    def update(self):
        pass

    # add toolbar and tile selector

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

        self.listerner.on_event("quit", quit)

        phase = Phase.get_current()
        phase.update()
        phase.render()

        self._display.blit(self.canvas, (0, 0))
        pygame.display.update()
        self._clock.tick(60)

if __name__ == "__main__":
    app = App()
    while True:
        app.main()
