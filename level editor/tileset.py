import pygame, os, json

def crop_image(surface, data):
    new_image = pygame.Surface((data[2], data[3]))
    new_image.blit(surface, (0, 0), data)
    return new_image

def load_set(dir, filename):
    path = os.path.join(dir, filename)
    image = pygame.image.load(path + ".png")
    meta_data = path + ".json"
    with open(meta_data) as file:
        data = json.load(file)

    tile_data = {}
    for name, frame in data["frames"].items():
        x, y = frame["frame"]["x"], frame["frame"]["y"]
        w, h = frame["frame"]["w"], frame["frame"]["h"]
        tile_data[name] = (x, y, w, h)

    tileset = {"fg": [], "bg": [], "dt": []}
    for name, tile in tile_data.items():
        tileset[name[:2]].append(crop_image(image, tile))

    return tileset
    
