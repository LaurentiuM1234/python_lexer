from Dfa import Dfa
from functools import reduce


class Lexer:
    def __init__(self):
        self.dfa_list = None
        self.word = None
        self.dfa_config_list = None

    def load_initial_configurations(self):
        self.dfa_config_list = \
            [(i.get_init_state(), -1, i.is_sink_state(i.get_init_state())) for i in self.dfa_list]

    def load_from_file(self, dfa_filepath, word_filepath):
        def load_automatas(filepath):
            def dfa_splitter(acc, crt):
                if crt == '':
                    acc.append([])
                else:
                    acc[-1].append(crt)
                return acc

            with open(filepath, "r") as fd:
                dfa_codifications = reduce(dfa_splitter, fd.read().split("\n"), [[]])
                dfa_list = list(map(lambda x: Dfa.build_from_codification(x),
                                    dfa_codifications))

            return dfa_list

        def load_word(filepath):
            with open(filepath, "r") as fd:
                return fd.read()

        # load list of dfas
        self.dfa_list = load_automatas(dfa_filepath)

        # load word
        self.word = load_word(word_filepath)

        # load initial configuration for each dfa
        self.load_initial_configurations()

    def load_from_dfa_list(self, dfa_list, word):
        self.dfa_list = dfa_list
        self.word = word
        # load initial configuration for each dfa
        self.load_initial_configurations()

    def run(self):
        def check_if_all_rejected():
            return reduce(lambda x, y: x and y[2], self.dfa_config_list, True)

        lexer_output = []
        end_pos = 0
        start_pos = 0
        char_index = 0

        while end_pos < len(self.word):
            for (idx, dfa) in enumerate(self.dfa_list):
                # if the current state the dfa is in is a sink state
                # don't bother updating its configuration
                if self.dfa_config_list[idx][2]:
                    continue

                # prepare configuration to feed to dfa
                config = (self.dfa_config_list[idx][0], self.word[end_pos])

                # get next configuration by performing step operation
                config = dfa.step(config)
                prev_cursor_pos = self.dfa_config_list[idx][1]

                if dfa.is_sink_state(config[0]):
                    # if current state is sink state, update configuration field
                    self.dfa_config_list[idx] = (config[0], prev_cursor_pos, True)
                    char_index = end_pos
                else:
                    if dfa.is_final_state(config[0]):
                        # if current state is final, update state and cursor position
                        self.dfa_config_list[idx] = (config[0], end_pos, False)
                    else:
                        # if current state is not final, only update sate
                        self.dfa_config_list[idx] = (config[0], prev_cursor_pos, False)

            if check_if_all_rejected() or\
                    (not check_if_all_rejected() and end_pos + 1 == len(self.word)):
                # extract list of all positions the dfas got stuck in
                positions = list(map(lambda x: x[1], self.dfa_config_list))

                # find index of max position
                max_idx = positions.index(max(positions))

                # extract max position
                max_pos = self.dfa_config_list[max_idx][1]

                if max_pos == -1:
                    # if the best position we found was -1 then we have a parse
                    # error

                    # compute list of newline character occurrences
                    newline_occurrences =\
                        [idx for (idx, char) in enumerate(self.word) if char == "\n"]

                    # compute line index from occurrence list
                    line_index = len(list(filter(lambda x: x < char_index, newline_occurrences)))

                    if check_if_all_rejected():
                        lexer_output = ["No viable alternative "
                                        "at character {}, "
                                        "line {}".format(char_index, line_index)]
                    else:
                        lexer_output = ["No viable alternative "
                                        "at character EOF, "
                                        "line {}".format(line_index)]
                    break
                else:
                    lexer_output.append((self.dfa_list[max_idx].get_token(),
                                         self.word[start_pos:max_pos + 1]))

                # update cursors
                start_pos = max_pos + 1
                end_pos = max_pos + 1

                # reset to initial configuration
                self.load_initial_configurations()
            else:
                end_pos += 1

        return lexer_output


def runlexer(dfa_filepath, in_filepath, out_filepath):
    lex = Lexer()
    lex.load_from_file(dfa_filepath, in_filepath)
    with open(out_filepath, "w") as fd:
        lexer_output = lex.run()

        if not isinstance(lexer_output[0], tuple):
            fd.write(lexer_output[0])
        else:
            for i in lexer_output:
                token = i[0]
                lexeme = i[1].replace("\n", "\\n")

                fd.write(token + " " + lexeme + "\n")
