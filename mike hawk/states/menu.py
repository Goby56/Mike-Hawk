from main import State
from states.game import Game

class Menu(State):
    def __init__(self, game):
        State.__init__(self, game)

    def update(self, dt, inputs):
        if inputs["lmb"]:
            new_state = Game(self.game)
            new_state.enter_state()
        self.game.reset_keys()


    def render(self, surface):
        surface.fill((200,200,200))