import pygame, json, os
from spritesheet import Spritesheet

base_dir = os.path.abspath(os.path.dirname(__file__))
map_dir = os.path.join(base_dir, "maps")

def load_map(filename):
    location = os.path.join(map_dir, ".json")
    with open(location) as file:
        json_dict = json.load(file)
    return json_dict, location


class App:
    def __init__(self):
        
        self.map, self.map_location = load_map("dev_level") # temp, make choise in app

    def main(self):
        pass

    def save(self):
        with open(self.map_location) as file:
            json.dump(self.map, file)


if __name__ == "__main__":
    app = App()
    while True:
        app.main()