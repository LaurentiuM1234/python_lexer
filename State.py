
class State:
    def __init__(self):
        self.components = []

    @staticmethod
    def build_from_string(string):
        state = State()

        # the list of components will be sorted because states such as
        # [1, 2, 3] and [3, 2, 1] are actually the same
        state.components = sorted(list(map(lambda x: int(x), string.split(","))))

        return state

    @staticmethod
    def build_from_int(value):
        state = State()

        state.components = [value]

        return state

    def get_component_states(self):
        return list(map(lambda x: State.build_from_int(x), self.components))

    def __contains__(self, item):
        return isinstance(item, State) and set(item.components).issubset(self.components)

    def __str__(self):
        return "".join(list(map(lambda x: str(x), self.components)))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, State):
            return False

        if len(self.components) != len(other.components):
            return False

        return self.components == other.components

    def __hash__(self):
        return hash(repr(self))

    def __add__(self, other):
        if isinstance(other, int):
            if len(self.components) == 1:
                return State.build_from_string(str(self.components[0] + other))
        elif isinstance(other, State):
            self.components = sorted(list(set(self.components + other.components)))
            return self

    def __lt__(self, other):
        if len(self.components) == 1 and len(other.components) == 1:
            return self.components[-1].__lt__(other.components[-1])
        else:
            return False
