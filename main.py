from Nfa import *
from Dfa import *
import sys


def convert_regex_to_dfa(input_file, output_file):
    with open(input_file, "r") as fd:
        regex = Regex.parse(fd.read())

    dfa = Dfa.build_from_nfa(Nfa.build_from_regex(regex))

    with open(output_file, "w") as fd:
        fd.write(str(dfa))


convert_regex_to_dfa(sys.argv[1], sys.argv[2])
