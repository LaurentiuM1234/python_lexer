from Stack import Stack
from itertools import chain


class Regex:
    @staticmethod
    def parse(string):
        stack = []

        # iterate through all the tokens found in given string
        # in order to build the regex
        for token in string.split(" "):
            if token == "CONCAT":
                stack.append(Concat(None, None))
            elif token == "UNION":
                stack.append(Union(None, None))
            elif token == "STAR":
                stack.append(Star(None))
            elif token == "PLUS":
                stack.append(Plus(None))
            else:
                stack.append(Var(token))

            crt_op = stack.pop()

            while True:
                # if currently extracted operator is not satisfied
                # then put it back in the stack and go to the next
                # token
                if not crt_op.is_satisfied():
                    stack.append(crt_op)
                    break
                else:
                    # if the stack is empty then we have finished the parsing process
                    if not stack:
                        return crt_op

                    # extract the previous operator found in the stack
                    # and apply it to current operator in order to try
                    # to satisfy it
                    prev_op = stack.pop()
                    prev_op.apply(crt_op)
                    crt_op = prev_op

        # if this point is reached then there was probably an error
        # during the parsing process
        return None

    @staticmethod
    def inverse_parse(token_list):
        # same as the @parse function but the arguments are applied in an inverse order
        # and the string has already been split
        stack = []

        # iterate through all the tokens found in given string
        # in order to build the regex
        for token in token_list:
            if token == "CONCAT":
                stack.append(Concat(None, None))
            elif token == "UNION":
                stack.append(Union(None, None))
            elif token == "STAR":
                stack.append(Star(None))
            elif token == "PLUS":
                stack.append(Plus(None))
            else:
                stack.append(Var(token))

            crt_op = stack.pop()

            while True:
                # if currently extracted operator is not satisfied
                # then put it back in the stack and go to the next
                # token
                if not crt_op.is_satisfied():
                    stack.append(crt_op)
                    break
                else:
                    # if the stack is empty then we have finished the parsing process
                    if not stack:
                        return crt_op

                    # extract the previous operator found in the stack
                    # and apply it to current operator in order to try
                    # to satisfy it
                    prev_op = stack.pop()
                    prev_op.inverse_apply(crt_op)
                    crt_op = prev_op

        # if this point is reached then there was probably an error
        # during the parsing process
        return None

    @staticmethod
    def tokenize(regex: str):
        # string that will replace the [a-z] alias
        expand_a_z = "(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)"

        # string that will replace the [0-9] alias
        expand_0_9 = "(0|1|2|3|4|5|6|7|8|9)"

        # expand [a-z]
        regex = regex.replace("[a-z]", expand_a_z)

        # expand [0-9]
        regex = regex.replace("[0-9]", expand_0_9)

        # add spaces between the parentheses and the following tokens
        regex = regex.replace("'('", "PAR").replace("(", " ( ").replace("PAR", "'('")
        regex = regex.replace("')'", "PAR").replace(")", " ) ").replace("PAR", "')'")

        # replace all operators with their string equivalents
        regex = regex.replace("'+'", "ESC").replace("+", " PLUS ").replace("ESC", "'+'")
        regex = regex.replace("'*'", "ESC").replace("*", " STAR ").replace("ESC", "'*'")
        regex = regex.replace("'|'", "ESC").replace("|", " UNION ").replace("ESC", "'|'")

        # remove extra whitespaces
        regex = ' '.join(regex.split())

        # transform regex into list of tokens
        regex = regex.replace("' '", "SPACE")
        tokens = regex.split(' ')
        tokens = list(map(lambda x: x.replace("SPACE", "' '"), tokens))

        # define a list of all special tokens
        specials = ["(", ")", "PLUS", "STAR", "UNION", "CONCAT"]

        # add the concatenation operator between symbols that are not operators in a token
        def concat_adder(string):
            if string in specials:
                # if the string is a special character (not an operand) then
                # do not modify it
                return [string]
            else:
                result = []

                i = 0
                while i < len(string):
                    if string[i] == "'" and i + 1 < len(string) and string[i + 1] != '\\':
                        # we have an "escaped" normal character
                        result.append(string[i:i + 3])

                        if i + 2 < len(string) - 1:
                            result.append("CONCAT")

                        i += 3
                    elif string[i] == "'" and i + 1 < len(string) and string[i + 1] == '\\':
                        # we have an "escaped" control character
                        result.append(string[i:i + 4])

                        if i + 3 < len(string) - 1:
                            result.append("CONCAT")

                        i += 4
                    else:
                        result.append(string[i])

                        if i < len(string) - 1:
                            result.append("CONCAT")

                        i += 1
            return result

        # apply the concatenation add function on each token in list
        tokens = list(map(concat_adder, tokens))

        # merge all the resulting lists
        tokens = list(chain(*tokens))

        # add the missing concatenation operators
        i = 0

        while i < len(tokens) - 1:
            if tokens[i] == ")" and tokens[i + 1] == "(":
                # add concat between ) and (
                tokens.insert(i + 1, "CONCAT")
                i += 2
            elif ((tokens[i] == "PLUS" or tokens[i] == "STAR")
                  and (tokens[i + 1] == "(" or tokens[i + 1] not in specials)):
                # add concat between PLUS/STAR and ( or a normal character
                tokens.insert(i + 1, "CONCAT")
                i += 2
            elif tokens[i] not in specials and tokens[i + 1] not in specials:
                # add concat between 2 normal characters
                tokens.insert(i + 1, "CONCAT")
                i += 2
            elif tokens[i] not in specials and tokens[i + 1] == "(":
                # add concat between a normal character and (
                tokens.insert(i + 1, "CONCAT")
                i += 2
            elif tokens[i] == ")" and tokens[i + 1] not in specials:
                # add concat between ) and a normal character
                tokens.insert(i + 1, "CONCAT")
                i += 2
            else:
                i += 1

        return tokens

    @staticmethod
    def to_prefix_form(regex: str):
        # transform the regex into a list of tokens that can be then easily parsed
        # in order to transform the regex into the prenex form
        token_list = Regex.tokenize(regex)

        # prepare required variables
        stack = Stack()
        operators = ["UNION", "CONCAT", "PLUS", "STAR"]

        # establish the precedence of the operators
        precedence = dict()
        precedence["("] = 0
        precedence["UNION"] = 1
        precedence["CONCAT"] = 2
        precedence["PLUS"] = 3
        precedence["STAR"] = 3

        result = []

        for token in token_list:
            if token not in operators and token != "(" and token != ")":
                result.append(token)
            elif token == "(":
                stack.push(token)
            elif token == ")":
                # remove all operators from operator stack until the ( is found
                while stack.peek() != "(":
                    result.append(stack.peek())
                    stack.pop()

                # remove ( from stack
                stack.pop()
            elif token in operators:
                if stack.is_empty():
                    stack.push(token)
                else:
                    # remove all operators that have a higher precedence than current operator
                    while (not stack.is_empty()) and precedence[stack.peek()] >= precedence[token]:
                        result.append(stack.pop())

                    stack.push(token)
            else:
                # found an unknown token
                return None

        # remove remaining operators from stack
        while not stack.is_empty():
            result.append(stack.pop())

        # reverse the list to bring it from postfix to prefix form
        result.reverse()

        return result


class Var(Regex):
    def __init__(self, symbol):
        super().__init__()
        if len(symbol) < 3:
            self.symbol = symbol
        else:
            if symbol[0] == '\'' and symbol[-1] == '\'':
                if symbol[1:-1] == "\\n":
                    self.symbol = '\n'
                elif symbol[1:-1] == "\\t":
                    self.symbol = '\t'
                else:
                    self.symbol = symbol[1:-1]
            else:
                self.symbol = symbol


    def is_satisfied(self):
        return self.symbol is not None

    def apply(self, symbol):
        self.symbol = symbol

    def inverse_apply(self, regex):
        self.apply(regex)

    def __str__(self):
        return str(self.symbol)

    def __repr__(self):
        return str(self)

    def get_symbol(self):
        return self.symbol


class Star(Regex):
    def __init__(self, regex):
        super().__init__()
        self.regex = regex

    def is_satisfied(self):
        return self.regex is not None

    def apply(self, regex):
        self.regex = regex

    def inverse_apply(self, regex):
        self.apply(regex)

    def __str__(self):
        return "Star(" + str(self.regex) + ")"

    def __repr__(self):
        return str(self)

    def get_regex(self):
        return self.regex


class Union(Regex):
    def __init__(self, l_regex, r_regex):
        super().__init__()
        self.l_regex = l_regex
        self.r_regex = r_regex

    def is_satisfied(self):
        return self.l_regex is not None and self.r_regex is not None

    def apply(self, regex):
        if self.l_regex is None:
            self.l_regex = regex
        elif self.r_regex is None:
            self.r_regex = regex

    def inverse_apply(self, regex):
        if self.r_regex is None:
            self.r_regex = regex
        elif self.l_regex is None:
            self.l_regex = regex

    def __str__(self):
        return "Union(" + str(self.l_regex) + "," + str(self.r_regex) + ")"

    def __repr__(self):
        return str(self)

    def get_left_regex(self):
        return self.l_regex

    def get_right_regex(self):
        return self.r_regex


class Plus(Regex):
    def __init__(self, regex):
        super().__init__()
        self.regex = regex

    def is_satisfied(self):
        return self.regex is not None

    def apply(self, regex):
        self.regex = regex

    def inverse_apply(self, regex):
        self.apply(regex)

    def __str__(self):
        return "Plus(" + str(self.regex) + ")"

    def __repr__(self):
        return str(self)

    def get_regex(self):
        return self.regex


class Concat(Regex):
    def __init__(self, l_regex, r_regex):
        super().__init__()
        self.l_regex = l_regex
        self.r_regex = r_regex

    def is_satisfied(self):
        return self.l_regex is not None and self.r_regex is not None

    def apply(self, regex):
        if self.l_regex is None:
            self.l_regex = regex
        elif self.r_regex is None:
            self.r_regex = regex

    def inverse_apply(self, regex):
        if self.r_regex is None:
            self.r_regex = regex
        elif self.l_regex is None:
            self.l_regex = regex

    def __str__(self):
        return "Concat(" + str(self.l_regex) + "," + str(self.r_regex) + ")"

    def __repr__(self):
        return str(self)

    def get_left_regex(self):
        return self.l_regex

    def get_right_regex(self):
        return self.r_regex
