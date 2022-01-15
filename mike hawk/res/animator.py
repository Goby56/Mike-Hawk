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
        self.sequence_index = 0
        self.previous_sequence_index = None
        self.delay = self.animation_delays[self.tag][self.sequence_index]

    def update(self, dt):
        if self.tag != self.previous_tag:
            self.counter = 0
        else: self.counter += 1
        
        index = self.animation_delays[self.tag][self.sequence_index]
        if type(index) != list:
            self.counter %= index
        self.sequence_index %= len(self.animation_delays[self.tag])
        
        self.previous_tag = self.tag

    def get_frame(self, tag):
        self.tag = tag
        delay = self.animation_delays[tag][self.sequence_index]
        if type(delay) is list:
            if self.sequence_index != self.previous_sequence_index:
                self.delay = random.randint(*delay)

        else: self.delay = delay

        if self.counter + 1 >= self.delay:
            self.previous_sequence_index = self.sequence_index
            self.sequence_index += 1
        self.sequence_index %= len(self.animation_delays[tag])
        return self.frames[tag][self.sequence_index]


    def set_frame(self, n, tag=None):
        pass



# class Animator:
#     """
#     The function of this class is to determine which frame
#     should be rendered. 
#     \nUse .create_values() to create a new instance of frames and delays
#     \nUse .get_frame() to get the current frame
#     """
#     def __init__(self):
#         self.frames_dict = dict()
#         # Stores the different components associated to the frames in 
#         # a dictionary which can be accessed by an identification

#     def create_values(self, identification, frames, delay):
#         self.frames_dict[identification] = {
#             "frames" : frames,
#             "delay" : delay,
#             "counter" : 0
#         }

#     def update(self):
#         for identification in self.frames_dict.keys():
#             components = self.frames_dict[identification]
#             components["counter"] += components["delay"]

#     def get_frame(self, identification):
#         components = self.frames_dict[identification]
#         return components["frames"][int(components["delay"]%len(components["frames"]))]


