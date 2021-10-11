import pygame, os, time

class Main:
    def __init__(self):
        pygame.init()
        self.WINDOW_W, self.WINDOW_H = 720, 576
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.WINDOW_W, self.WINDOW_H))
        self.running = True
        self.inputs = {
            "w":False,
            "a":False,
            "s":False,
            "d":False,
            "space":False,
            "escape":False,
            "enter":False,
            "lmb":False,
            "rmb":False
        } 
        self.dt, self.previous_time = 0, 0
        self.state_stack = []
        self.load_assets()
        self.load_states()

    def main_loop(self):
        self.get_dt()
        self.capture_inputs()
        self.update()
        self.render()
        
        self.clock.tick(60)

    def update(self):
        self.state_stack[-1].update(self.dt, self.inputs)

    def render(self):
        self.state_stack[-1].render(self.screen)
        pygame.display.update()

    def get_dt(self):
        current_time = time.time()
        self.dt = current_time - self.previous_time
        self.previous_time = current_time

    def draw_text(self):
        pass

    def load_assets(self):
        self.assets_directory = os.path.join("assets")

    def load_states(self):
        from states.menu import Menu
        self.state_stack.append(Menu(self))

    def capture_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.inputs["w"] = True 
                if event.key == pygame.K_a:
                    self.inputs["a"] = True 
                if event.key == pygame.K_s:
                    self.inputs["s"] = True 
                if event.key == pygame.K_d:
                    self.inputs["d"] = True 
                if event.key == pygame.K_SPACE:
                    self.inputs["space"] = True
                if event.key == pygame.K_ESCAPE:
                    self.inputs["escape"] = True  
                if event.key == pygame.K_RETURN:
                    self.inputs["return"] = True  
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.inputs["w"] = False
                if event.key == pygame.K_a:
                    self.inputs["a"] = False
                if event.key == pygame.K_s:
                    self.inputs["s"] = False
                if event.key == pygame.K_d:
                    self.inputs["d"] = False
                if event.key == pygame.K_SPACE:
                    self.inputs["space"] = False
                if event.key == pygame.K_ESCAPE:
                    self.inputs["escape"] = False 
                if event.key == pygame.K_RETURN:
                    self.inputs["return"] = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.inputs["lmb"] = True
                if event.button == 3:
                    self.inputs["rmb"] = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.inputs["lmb"] = False
                if event.button == 3:
                    self.inputs["rmb"] = False

    def reset_keys(self):
        for event in self.inputs:
            self.inputs[event] = False


class State:
    def __init__(self, game):
        self.game = game
        self.previous_state = None

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.previous_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()


if __name__ == "__main__":
    game = Main()
    while game.running:
        game.main_loop()