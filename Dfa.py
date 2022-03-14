from functools import reduce
from Delta import Delta
from State import State


class Dfa:
    def __init__(self):
        self.alphabet = None
        self.token = None
        self.init_state = None
        self.final_states = None
        self.state_set = None
        self.delta = None
        self.sink_states = None

    @staticmethod
    def build_from_codification(codification):
        dfa = Dfa()

        # extract alphabet
        dfa.alphabet = codification[0]

        # extract token
        dfa.token = codification[1]

        # extract initial state - set of integers
        dfa.init_state = State.build_from_string(codification[2])

        # extract set of final states
        dfa.final_states = list(map(lambda x: State.build_from_string(x),
                                    codification[-1].split(" ")))

        # extract set of states
        def build_state_set():
            # extract list of transitions
            trans_list = list(map(lambda x: x.split(","), codification[3:-1]))

            # function used to insert states into the accumulator that aren't
            # already there
            def state_insertion(acc, crt):
                if State.build_from_string(crt[0]) not in acc:
                    acc.append(State.build_from_string(crt[0]))

                if State.build_from_string(crt[2]) not in acc:
                    acc.append(State.build_from_string(crt[2]))

                return acc

            return reduce(state_insertion, trans_list, [])

        dfa.state_set = build_state_set()

        # build delta function
        def build_delta():
            # transform every transition into a list
            trans_list = list(map(lambda x: x.split(","), codification[3:-1]))

            return Delta(trans_list)

        dfa.delta = build_delta()

        def compute_sink_states():
            reachable_states = []

            # reverse the transitions
            dfa.delta.reverse()

            def dfs(node):
                # extract all states we can go to from current node
                to_states = dfa.delta.get_transitions(node, None)

                # if there are any states we can go to, iterate through
                # each one of them and start search
                if to_states is not None:
                    for neigh in to_states:
                        if visited[neigh] == 0:
                            visited[neigh] = 1

                            if neigh not in reachable_states:
                                reachable_states.append(neigh)

                            dfs(neigh)

            for i in dfa.final_states:
                # build dictionary of visited states
                visited = dict()

                for j in dfa.state_set:
                    visited[j] = 0

                # start search from current final state
                dfs(i)

            # undo reverse operation
            dfa.delta.reverse()

            sink_states = list(set(dfa.state_set)
                               - set(reachable_states)
                               - set(dfa.final_states))

            return sink_states

        dfa.sink_states = compute_sink_states()

        return dfa

    @staticmethod
    def build_from_nfa(nfa, token="DFA"):
        dfa = Dfa()
        dfa.final_states = []
        dfa.token = token
        dfa.delta = Delta([])
        dfa.sink_states = [State.build_from_int(-1)]
        dfa.alphabet = nfa.get_alphabet()

        # add necessary transitions for sink state
        for symbol in dfa.alphabet:
            dfa.delta.add_transition([dfa.sink_states[0], symbol, dfa.sink_states[0]])

        # compute the eps-closure for each state in the NFA
        def compute_closure_dictionary():
            def dfs(crt, state_list):
                # no epsilon transitions, just return
                if nfa.get_delta().get_transitions(crt, "eps") is None:
                    return

                for neigh in nfa.get_delta().get_transitions(crt, "eps"):
                    if neigh not in state_list:
                        state_list.append(neigh)
                        dfs(neigh, state_list)

            result = dict()

            for state in nfa.get_state_set():
                # initially add just the state to the list
                result[state] = [state]

                # prepare a list containing all states reachable
                # from current state using epsilon-transitions
                eps_state_list = []

                # compute list of states reachable using eps-transitions
                dfs(state, eps_state_list)

                # append resulting list to current state's eps-closure
                result[state] += eps_state_list

            return result

        closure_dict = compute_closure_dictionary()

        # build DFA's initial state by using NFA's initial state's eps-closure
        init_state = reduce(lambda x, y: x + y, closure_dict[nfa.get_init_state()], State())

        dfa.init_state = init_state
        dfa.state_set = [init_state]

        # if the initial state contains the final state of the NFA then
        # add it to the set of final states for the DFA
        if nfa.get_final_states()[-1] in init_state:
            dfa.final_states.append(init_state)

        # iterate through the DFA's state set and new states and
        # transitions on the go
        for state in dfa.state_set:
            # iterate through each symbol in order to
            # add new states and transitions made on that
            # symbol
            for symbol in dfa.alphabet:
                # iterate through each component of the state
                # and find the reachable states on given symbol
                reachable_states = []

                for component in state.components:
                    transitions = nfa.get_delta() \
                        .get_transitions(State.build_from_int(component), symbol)

                    if transitions is not None:
                        # map every state in transition list to its eps-closure
                        transition_closures = list(map(lambda x: closure_dict[x.get_component_states()[0]],
                                                       transitions))

                        # merge the elements found in the list of closures and append
                        # the result to reachable states list
                        reachable_states += reduce(lambda x, y: x + y,
                                                   transition_closures,
                                                   [])

                if reachable_states:
                    # remove duplicate states if any
                    reachable_states = list(set(reachable_states))

                    # create a single state out of all the reachable states
                    reachable_state = reduce(lambda x, y: x + y, reachable_states, State())

                    # check if the new state contains NFA's final state
                    if nfa.get_final_states()[-1] in reachable_state:
                        if reachable_state not in dfa.final_states:
                            dfa.final_states.append(reachable_state)

                    # add the new state to state set
                    if reachable_state not in dfa.state_set:
                        dfa.state_set.append(reachable_state)

                    # add a new transition from current state to reachable state
                    dfa.delta.add_transition([state, symbol, reachable_state])
                else:
                    # add transition to sink state
                    dfa.delta.add_transition([state, symbol, dfa.sink_states[0]])

        # add sink state to state set
        dfa.state_set.append(State.build_from_int(-1))

        # build state remapping dictionary
        state_counter = 0

        state_map_dictionary = dict()

        for state in dfa.state_set:
            state_map_dictionary[state] = State.build_from_int(state_counter)
            state_counter += 1

        dfa.init_state = state_map_dictionary[dfa.init_state]
        dfa.final_states = list(map(lambda x: state_map_dictionary[x], dfa.final_states))
        dfa.state_set = list(map(lambda x: state_map_dictionary[x], dfa.state_set))
        dfa.sink_states = list(map(lambda x: state_map_dictionary[x], dfa.sink_states))
        dfa.delta.remap_states(state_map_dictionary)
        dfa.delta.sort()
        dfa.alphabet.sort()

        return dfa

    def __str__(self):
        alphabet = "".join(self.alphabet) + "\n"
        token = self.token + "\n"
        state_count = str(len(self.state_set)) + "\n"
        init_state = str(self.init_state) + "\n"
        final_states = " ".join(list(map(lambda x: str(x), self.final_states)))

        return alphabet + token + init_state + str(self.delta) + final_states

    def __repr__(self):
        return str(self)

    def step(self, config):
        state = config[0]
        word = config[1]

        next_state = self.delta.get_transitions(state, word[0])

        if state in self.sink_states and next_state is None:
            return state, word[1:]
        elif state not in self.sink_states and next_state is None:
            # check to see if there are any sink states and return
            # the first one in the set
            if len(self.sink_states) != 0:
                return self.sink_states[0], word
            else:
                # if there are no sink states, create a new one and
                # return it
                self.sink_states.append(State.build_from_string("-1"))
                return State.build_from_string("-1"), word
        else:
            return next_state[0], word[1:]

    def accepts_word(self, word):
        config = (self.init_state, word)

        while len(config[1]) >= 1:
            config = self.step(config)

            if config is None:
                return False

        if config[0] in self.sink_states or config[0] not in self.final_states:
            return False
        else:
            return True

    def get_init_state(self):
        return self.init_state

    def is_sink_state(self, state):
        return state in self.sink_states

    def is_final_state(self, state):
        return state in self.final_states

    def get_token(self):
        return self.token
