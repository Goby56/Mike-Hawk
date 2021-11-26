import pygame, sys, time
sys.path.append("..")

class Animator:
    """
    The function of this class is to determine which frame
    should be rendered. 
    \nUse .create_values() to create a new instance of frames and delays
    \nUse .get_frame() to get the current frame
    """
    def __init__(self):
        self.frames_dict = dict()
        # Stores the different components associated to the frames in 
        # a dictionary which can be accessed by an identification

    def create_values(self, identification, frames, delay):
        self.frames_dict[identification] = {
            "frames" : frames,
            "delay" : delay,
            "counter" : 0
        }

    def update(self):
        for identification in self.frames_dict.keys():
            components = self.frames_dict[identification]
            components["counter"] += components["delay"]

    def get_frame(self, identification):
        components = self.frames_dict[identification]
        return components["frames"][int(components["delay"]%len(components["frames"]))]


