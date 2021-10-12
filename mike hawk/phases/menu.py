from main import Phase

class Menu(Phase):
    def __init__(self, canvas, listener, dt):
        self.canvas, self.listener, self.dt = canvas, listener, dt
        