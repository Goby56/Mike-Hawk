import sys, os, time, json, pprint, random
sys.path.append("..")
from .spritesheet import Spritesheet
from .config import _base_dir

class Animator:
    """
    Provides an easy way to access which frame should be displayed 
    """
    instances = []

    def __init__(self, filename, starting_animation):
        self.frames = Spritesheet.instances[filename].frames
        self.counter = 0
        self.instances.append(self)
        with open(os.path.join(_base_dir, "animation_delays.json"), "r") as f:
            self.animation_delays = json.load(f)[filename]
        self.tag = starting_animation
        self.previous_tag = self.tag
        self.index = 0
        self.previous_index = None
        self.delay = self.animation_delays[self.tag][self.index]

    def update(self):
        if self.tag != self.previous_tag:
            self.counter = 0
            self.index = 0
        
        self.index %= len(self.animation_delays[self.tag])
        index = self.animation_delays[self.tag][self.index]
        if type(index) != list:
            self.counter %= index
        
        self.previous_tag = self.tag

    def increment(self, dt):
        self.counter += 1

    def get_frame(self, tag):
        self.tag = tag
        self.update()
        delay = self.animation_delays[tag][self.index]
        if type(delay) is list:
            if self.index != self.previous_index:
                self.delay = random.randint(*delay)

        else: self.delay = delay

        if self.counter + 1 >= self.delay:
            self.previous_index = self.index
            self.index += 1
        self.index %= len(self.animation_delays[tag])

        return self.frames[tag][self.index]

    def set_frame(self, n, tag=None):
        pass


