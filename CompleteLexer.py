from Regex import *
from Dfa import *
from Nfa import *
from Lexer import *
from AST import *


def load_dfa_list(lex_file):
    result = []

    # open specification file
    with open(lex_file, "r") as fd:
        content = fd.read().split(";\n")

        for line in content[:-1]:
            # extract DFA's token
            dfa_token = line[:line.find(' ')]

            # build the regex
            regex_string = line[line.find(' ') + 1:]
            regex = Regex.inverse_parse(Regex.to_prefix_form(regex_string))

            # build the DFA
            dfa = Dfa.build_from_nfa(Nfa.build_from_regex(regex), dfa_token)

            # add dfa to list of DFAs
            result.append(dfa)

    return result


def runcompletelexer(lex_file, input_file, output_file):
    dfa_list = []
    word = None

    with open(input_file, "r") as fd:
        word = fd.read()

    dfa_list = load_dfa_list(lex_file)

    # prepare lexer
    lexer = Lexer()
    lexer.load_from_dfa_list(dfa_list, word)

    with open(output_file, "w") as fd:
        lexer_output = lexer.run()

        if not isinstance(lexer_output[0], tuple):
            fd.write(lexer_output[0])
        else:
            for i in lexer_output:
                token = i[0]
                lexeme = i[1].replace("\n", "\\n")

                fd.write(token + " " + lexeme + "\n")


def runparser(input_file, output_file):
    dfa_list = []
    word = None

    with open(input_file, "r") as fd:
        word = fd.read()

    # load the DFA list from the language's specification file
    dfa_list = load_dfa_list("imp.spec")

    # prepare lexer
    lexer = Lexer()
    lexer.load_from_dfa_list(dfa_list, word)

    # run lexer
    lexer_output = lexer.run()

    # build AST from lexer output
    ast = prepare_ast(lexer_output)

    with open(output_file, "w") as fd:
        fd.write(str(ast))

def runinterpreter(input_file):
    dfa_list = []
    word = None

    with open(input_file, "r") as fd:
        word = fd.read()

    # load the DFA list from the language's specification file
    dfa_list = load_dfa_list("imp.spec")

    # prepare lexer
    lexer = Lexer()
    lexer.load_from_dfa_list(dfa_list, word)

    # run lexer
    lexer_output = lexer.run()

    # build AST from lexer output
    ast = prepare_ast(lexer_output)

    symbol_dict = dict()

    evaluate_ast(ast, symbol_dict)

    return symbol_dict





