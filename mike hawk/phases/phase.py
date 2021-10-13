class Phase:
    phase_stack = []

    @classmethod
    def get_current(cls):
        return cls.phase_stack[-1]

    def enter_phase(self): # Enters a new phase
        Phase.phase_stack.append(self)

    def exit_phase(self): # Exits to the previous state
        Phase.phase_stack.pop()

    def update(self):
        pass

    def render(self):
        pass