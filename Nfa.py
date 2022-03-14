from functools import reduce

from Delta import *
from Regex import *


class Nfa:
    def __init__(self, codification):
        # extract alphabet
        self.alphabet = [codification[0]]

        # extract token
        self.token = codification[1]

        # extract initial state - set of integers
        self.init_state = State.build_from_string(codification[2])

        # extract set of final states
        self.final_states = list(map(lambda x: State.build_from_string(x),
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

        self.state_set = build_state_set()

        # build delta function
        def build_delta():
            # transform every transition into a list
            trans_list = list(map(lambda x: x.split(","), codification[3:-1]))

            return Delta(trans_list)

        self.delta = build_delta()

    def get_delta(self):
        return self.delta

    def set_init_state(self, init_state):
        self.init_state = init_state

    def get_alphabet(self):
        return self.alphabet

    def add_symbol_to_alphabet(self, symbol):
        if symbol not in self.alphabet:
            self.alphabet.append(symbol)

    def add_transition(self, transition):
        self.delta.add_transition(transition)

    def add_final_state(self, final_state):
        self.final_states.append(final_state)

    def get_final_states(self):
        return self.final_states

    def add_to_state_set(self, state_list):
        for state in state_list:
            if state not in self.state_set:
                self.state_set.append(state)

    def get_state_set(self):
        return self.state_set

    def get_init_state(self):
        return self.init_state

    def set_final_states(self, final_states):
        self.final_states = final_states

    def star(self, max_state):
        # extract the previous final and initial states
        prev_init = self.init_state
        prev_final = self.final_states.pop()

        # build a new state and mark it as initial state
        new_init = State.build_from_int(max_state[0] + 1)
        self.init_state = new_init

        # build a new state and mark it as final state
        new_final = State.build_from_int(max_state[0] + 2)
        self.final_states = [new_final]

        max_state[0] = max_state[0] = max_state[0] + 2

        # add the new states
        self.add_to_state_set([new_init, new_final])

        # add required transitions
        self.add_transition([new_init, "eps", prev_init])
        self.add_transition([prev_final, "eps", new_final])
        self.add_transition([new_init, "eps", new_final])
        self.add_transition([prev_final, "eps", prev_init])

        # return the result NFA
        return self

    def plus(self, max_state):
        # extract the previous final and initial states
        prev_init = self.init_state
        prev_final = self.final_states.pop()

        # build a new state and mark it as initial state
        new_init = State.build_from_int(max_state[0] + 1)
        self.init_state = new_init

        # build a new state and mark it as final state
        new_final = State.build_from_int(max_state[0] + 2)
        self.final_states = [new_final]

        max_state[0] = max_state[0] = max_state[0] + 2

        # add the new states
        self.add_to_state_set([new_init, new_final])

        # add required transitions
        self.add_transition([new_init, "eps", prev_init])
        self.add_transition([prev_final, "eps", new_final])
        self.add_transition([prev_final, "eps", prev_init])

        # return the result NFA
        return self

    def concat(self, other):
        # extract final state for first NFA
        nfa1_final = self.final_states[-1]

        # extract final and initial states for second NFA
        nfa2_init = other.init_state
        nfa2_final = other.final_states[-1]

        # merge the 2 NFAs
        self.__add__(other)

        # set the new final state
        self.final_states = [nfa2_final]

        # add required transitions
        self.add_transition([nfa1_final, "eps", nfa2_init])

        return self

    def union(self, other, max_state):
        # extract final and initial states for first NFA
        nfa1_init = self.init_state
        nfa1_final = self.final_states[-1]

        # extract final and initial states for second NFA
        nfa2_init = other.init_state
        nfa2_final = other.final_states[-1]

        # merge the 2 NFAs
        self.__add__(other)

        # create new initial state
        new_init = State.build_from_int(max_state[0] + 1)
        self.init_state = new_init

        # create new final state
        new_final = State.build_from_int(max_state[0] + 2)
        self.final_states = [new_final]

        max_state[0] = max_state[0] + 2

        # add states to state set
        self.add_to_state_set([new_init, new_final])

        # add required transitions
        self.add_transition([new_init, "eps", nfa1_init])
        self.add_transition([new_init, "eps", nfa2_init])
        self.add_transition([nfa2_final, "eps", new_final])
        self.add_transition([nfa1_final, "eps", new_final])

        return self

    def __add__(self, other):
        if not isinstance(other, Nfa):
            return None

        # merge the alphabets
        self.alphabet = list(set(self.alphabet).union(set(other.alphabet)))

        # merge the final state sets
        self.final_states = list(set(self.final_states).union(set(other.final_states)))

        # merge the state sets
        self.state_set = list(set(self.state_set).union(set(other.state_set)))

        # merge the deltas
        self.delta = self.delta + other.delta

        return self

    @staticmethod
    def build_from_regex(regex):
        # prepare a list with a single element used to keep track
        # of the max state value in order to avoid state collision
        max_state = [-1]

        return Nfa.build_from_regex_helper(max_state, regex)

    @staticmethod
    def build_from_regex_helper(max_state, regex):
        if isinstance(regex, Var):
            # compute new initial and final states
            init_state = max_state[0] + 1
            final_state = max_state[0] + 2

            # update the value of the max state
            max_state[0] = max_state[0] + 2

            return Nfa([regex.get_symbol(),
                        "NFA",
                        str(init_state),
                        str(init_state) + ",'" + regex.get_symbol() + "'," + str(final_state),
                        str(final_state)])
        elif isinstance(regex, Star):
            return Nfa.build_from_regex_helper(max_state, regex.get_regex()).star(max_state)
        elif isinstance(regex, Plus):
            return Nfa.build_from_regex_helper(max_state, regex.get_regex()).plus(max_state)
        elif isinstance(regex, Concat):
            left_nfa = Nfa.build_from_regex_helper(max_state, regex.get_left_regex())
            right_nfa = Nfa.build_from_regex_helper(max_state, regex.get_right_regex())

            return left_nfa.concat(right_nfa)
        elif isinstance(regex, Union):
            left_nfa = Nfa.build_from_regex_helper(max_state, regex.get_left_regex())
            right_nfa = Nfa.build_from_regex_helper(max_state, regex.get_right_regex())

            return left_nfa.union(right_nfa, max_state)

    def __str__(self):
        alphabet = "ALPHABET: " + str(self.alphabet) + "\n"
        token = "TOKEN: " + self.token + "\n"
        init_state = "INITIAL STATE: " + str(self.init_state) + "\n"
        final_states = "FINAL STATES: " + str(self.final_states) + "\n"
        state_set = "STATE SET: " + str(self.state_set) + "\n"

        return alphabet + token + init_state + final_states + state_set + str(self.delta)
