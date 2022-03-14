from State import State


class Delta:
    def __init__(self, transition_list):
        # transition_list is a list of lists, each element having the following
        # format: [from_state, symbol, to_state], where from_state is a string
        # containing multiple integers, symbol is a simple string and to_state
        # has the same format as from_state

        def build_state_list(idx):
            state_list = list(map(lambda x: State.build_from_string(x[idx]), transition_list))

            return state_list

        # the from_states can be found at index 0 of every transition
        self.from_state_list = build_state_list(0)

        def symbol_adder(x):
            if x[1][1:-1] == "\\n":
                return "\n"
            else:
                return x[1][1:-1]

        # extract symbols while removing redundant '' characters
        self.symbol_list = list(map(symbol_adder, transition_list))

        # the from states can be found at index 2 of every transition
        self.to_state_list = build_state_list(2)

    def add_transition(self, transition):
        # transition = [from_state, symbol, to_state]
        from_state = transition[0]
        symbol = transition[1]
        to_state = transition[2]

        self.from_state_list.append(from_state)
        self.symbol_list.append(symbol)
        self.to_state_list.append(to_state)

    def __str__(self):
        string_rep = ""
        for i in range(0, len(self.symbol_list)):
            string_rep += str(self.from_state_list[i]) \
                          + ",'" + self.symbol_list[i] \
                          + "'," + str(self.to_state_list[i]) \
                          + "\n"

        return string_rep

    def get_transitions(self, state, symbol):
        if symbol is None:
            # look for any transitions from provided state
            result = list(filter(lambda x: x[0] == state,
                                 zip(self.from_state_list, self.symbol_list, self.to_state_list)))

            # only leave out the to_states in the result list
            result = list(map(lambda x: x[2], result))

            if not result:
                # no matching entry
                return None
            else:
                # return to_state list
                return result
        else:
            # look for entries of format (state, symbol, _)
            result = list(filter(lambda x: x[0] == state and x[1] == symbol,
                                 zip(self.from_state_list, self.symbol_list, self.to_state_list)))

            # only leave out the to_states in the result list
            result = list(map(lambda x: x[2], result))

            if not result:
                # no matching entry
                return None
            else:
                # return to_state list
                return result

    def reverse(self):
        tmp = self.from_state_list
        self.from_state_list = self.to_state_list
        self.to_state_list = tmp

    def __add__(self, other):
        if not isinstance(other, Delta):
            return None

        self.from_state_list, self.symbol_list, self.to_state_list \
            = zip(*list(set(zip(self.from_state_list, self.symbol_list, self.to_state_list))
                        .union(set(zip(other.from_state_list, other.symbol_list, other.to_state_list)))))

        # convert the class variables back to lists
        self.from_state_list = list(self.from_state_list)
        self.symbol_list = list(self.symbol_list)
        self.to_state_list = list(self.to_state_list)

        return self

    def remap_states(self, state_map_dictionary):
        self.from_state_list = list(map(lambda x: state_map_dictionary[x],
                                        self.from_state_list))
        self.to_state_list = list(map(lambda x: state_map_dictionary[x],
                                      self.to_state_list))

    def sort(self):
        transitions = list(zip(self.from_state_list, self.symbol_list, self.to_state_list))

        transitions.sort()

        self.from_state_list, self.symbol_list, self.to_state_list = zip(*transitions)
