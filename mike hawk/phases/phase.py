class Phase:
    phase_stack = []

    @classmethod
    def get_current(cls):
        return cls.phase_stack[-1]

    def enter_phase(self): # Enters a new phase
        Phase.phase_stack.append(self)

    def exit_phase(self, amount=1): # Exits to the previous state
            Phase.phase_stack = Phase.phase_stack[:-amount]

    def update(self, *args, **kwargs):
        pass

    def render(self):
        pass