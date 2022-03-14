from Stack import *

TAB = '  '  # two whitespaces


class Node:
    def __init__(self, *args):
        self.height = int(args[0])  # the level of indentation required for current Node

    def __str__(self):
        return 'prog'

    @staticmethod
    def one_tab(line):
        """Formats the line of an argument from an expression."""
        return TAB + line + '\n'

    def final_print_str(self, print_str):
        """Adds height number of tabs at the beginning of every line that makes up the current Node."""
        return (self.height * TAB).join(print_str)


class InstructionList(Node):
    """begin <instruction_list> end"""

    def __init__(self, *args):  # args = height, [Nodes in instruction_list]
        super().__init__(args[0])
        self.list = args[1]
        self.satisfied = False

    def __str__(self):
        print_str = ['[\n']
        for expr in self.list:
            print_str.append(self.one_tab(expr.__str__()))
        print_str.append(']')

        return self.final_print_str(print_str)

    def is_satisfied(self):
        return self.satisfied


class Expr(Node):
    """<expr> + <expr> | <expr> - <expr> | <expr> * <expr> | <expr> > <expr> | <expr> == <expr> | <variable> | <integer>"""

    def __init__(self, *args):  # args = height, '+' | '-' | '*' | '>' | '==' | 'v' | 'i', left_side, *right_side
        super().__init__(args[0])
        self.type = args[1]
        self.left = args[2]
        if len(args) > 3:
            self.right = args[3]
        else:
            # variable and integer have no right_side
            self.right = None

    def apply(self, expr):
        if self.type != 'v' and self.type != 'i':
            if self.right is None:
                self.right = expr
            elif self.left is None:
                self.left = expr
        else:
            self.left = expr

    def is_satisfied(self):
        if self.type == 'v' or self.type == 'i':
            return True
        else:
            return self.left is not None and self.right is not None

    def __str__(self):
        name = 'expr'
        if self.type == 'v':
            name = 'variable'
        elif self.type == 'i':
            name = 'integer'
        elif self.type == '+':
            name = 'plus'
        elif self.type == '-':
            name = 'minus'
        elif self.type == '*':
            name = 'multiply'
        elif self.type == '>':
            name = 'greaterthan'
        elif self.type == '==':
            name = 'equals'

        print_str = [name + ' [\n', self.one_tab(str(self.left))]
        if self.right:
            print_str.append(self.one_tab(str(self.right)))
        print_str.append(']')

        return self.final_print_str(print_str)


class While(Node):
    """while (<expr>) do <prog> od"""

    def __init__(self, *args):  # args = height, Node_expr, Node_prog
        super().__init__(args[0])
        self.expr = args[1]
        self.prog = args[2]
        self.satisfied = False

    def __str__(self):
        print_str = ['while [\n',
                     self.one_tab(self.expr.__str__()),
                     self.one_tab('do ' + self.prog.__str__()),
                     ']']
        return self.final_print_str(print_str)

    def is_satisfied(self):
        return self.satisfied


class If(Node):
    """if (<expr>) then <prog> else <prog> fi"""

    def __init__(self, *args):  # args = height, Node_expr, Node_then, Node_else
        super().__init__(args[0])
        self.expr = args[1]
        self.then_branch = args[2]
        self.else_branch = args[3]
        self.then_satisfied = False
        self.else_satisfied = False

    def __str__(self):
        print_str = ['if [\n',
                     self.one_tab(self.expr.__str__()),
                     self.one_tab('then ' + self.then_branch.__str__()),
                     self.one_tab('else ' + self.else_branch.__str__()),
                     ']']
        return self.final_print_str(print_str)

    def is_satisfied(self):
        return self.expr is not None and self.then_satisfied and self.else_satisfied


class Assign(Node):
    """<variable> '=' <expr>"""

    def __init__(self, *args):  # args = height, Node_variable, Node_expr
        super().__init__(args[0])
        self.variable = args[1]
        self.expr = args[2]

    def __str__(self):
        print_str = ['assign [\n',
                     self.one_tab(self.variable.__str__()),
                     self.one_tab(self.expr.__str__()),
                     ']']
        return self.final_print_str(print_str)

    def __repr__(self):
        return self.__str__()

    def is_satisfied(self):
        return self.expr is not None and self.variable is not None

    def apply(self, expr):
        if self.variable is None:
            self.variable = expr
        elif self.expr is None:
            self.expr = expr


def convert_expression(expr: str):
    result = []

    # split expression into tokens
    token_list = expr.split(' ')

    # prepare required variables
    stack = Stack()
    operators = ["-", "+", ">", "*", "=="]

    # establish the precedence of the operators
    precedence = dict()
    precedence[">"] = 0
    precedence["=="] = 1
    precedence["+"] = 2
    precedence["-"] = 2
    precedence["*"] = 3

    result = []

    for token in token_list:
        if token not in operators and token != "(" and token != ")":
            result.append(token)
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


def parse_expression(height, expr: list):
    stack = []
    operators = ["-", "+", "*", "==", ">"]

    # iterate through all the tokens found in given string
    # in order to build the regex
    # in order to build the regex
    for token in expr:
        if token in operators:
            stack.append(Expr(height, token, None, None))
        else:
            if token[0] == '-':
                if token[1:].isnumeric():
                    stack.append(Expr(height, 'i', token))
                else:
                    stack.append(Expr(height, 'v', token))
            else:
                if token.isnumeric():
                    stack.append(Expr(height, 'i', token))
                else:
                    stack.append(Expr(height, 'v', token))

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


def build_ast(lexer_output):
    stack = []

    # iterate through all the tokens found in given string
    # in order to build the regex
    # in order to build the regex
    for token in lexer_output:
        if token[0] == "EXPR":
            # if the token is an expression, create an expression node and add it to stack
            stack.append(parse_expression(0, convert_expression(token[1])))
        elif token[0] == "ASSIGN":
            stack.append(Assign(0, Expr(0, 'v', token[1].replace("=", '').replace(' ', '')), None))
        elif token[0] == "KEYWORDS":
            if token[1] == "if":
                stack.append(If(0, None, None, None))
            elif token[1] == "while":
                stack.append(While(0, None, None))
            elif token[1] == "begin":
                stack.append(InstructionList(0, []))
            elif token[1] == "else":
                stack[-1].then_satisfied = True
            elif token[1] == "fi":
                stack[-1].else_satisfied = True
            elif token[1] == "od" or token[1] == "end":
                stack[-1].satisfied = True

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
                if isinstance(prev_op, Assign):
                    prev_op.expr = crt_op
                elif isinstance(prev_op, InstructionList):
                    prev_op.list.append(crt_op)
                elif isinstance(prev_op, If):
                    if prev_op.expr is None:
                        prev_op.expr = crt_op
                    elif not prev_op.then_satisfied:
                        if prev_op.then_branch is None:
                            prev_op.then_branch = crt_op
                        else:
                            if isinstance(prev_op.then_branch, list):
                                prev_op.then_branch.append(crt_op)
                            else:
                                prev_op.then_branch = [prev_op.then_branch, crt_op]

                    elif not prev_op.else_satisfied:
                        if prev_op.else_branch is None:
                            prev_op.else_branch = crt_op
                        else:
                            if isinstance(prev_op.else_branch, list):
                                prev_op.else_branch.append(crt_op)
                            else:
                                prev_op.else_branch = [prev_op.else_branch, crt_op]
                elif isinstance(prev_op, While):
                    if prev_op.expr is None:
                        prev_op.expr = crt_op
                    else:
                        if prev_op.prog is None:
                            prev_op.prog = crt_op
                        else:
                            if isinstance(prev_op.prog, list):
                                prev_op.prog.append(crt_op)
                            else:
                                prev_op.prog = [prev_op.prog, crt_op]

                crt_op = prev_op

    # if this point is reached then there was probably an error
    # during the parsing process
    return None


def format_ast(height, node):
    if isinstance(node, InstructionList):
        for i in node.list:
            format_ast(height + 1, i)
    elif isinstance(node, If):
        format_ast(height + 1, node.expr)

        if isinstance(node.then_branch, list):
            for i in node.then_branch:
                format_ast(height + 1, i)
        else:
            format_ast(height + 1, node.then_branch)

        if isinstance(node.else_branch, list):
            for i in node.else_branch:
                format_ast(height + 1, i)
        else:
            format_ast(height + 1, node.else_branch)
    elif isinstance(node, While):
        format_ast(height + 1, node.expr)
        if isinstance(node.prog, list):
            for i in node.prog:
                format_ast(height + 1, i)
        else:
            format_ast(height + 1, node.prog)
    elif isinstance(node, Assign):
        format_ast(height + 1, node.expr)
        format_ast(height + 1, node.variable)
    elif isinstance(node, Expr):
        if node.left is not None and isinstance(node.left, Expr):
            format_ast(height + 1, node.left)

        if node.right is not None and isinstance(node.right, Expr):
            format_ast(height + 1, node.right)

    node.height = height


def prepare_ast(lexer_output):
    ast = build_ast(lexer_output)

    format_ast(0, ast)

    return ast


def eval_expression(expr: Expr, symbol_dict):
    if expr.type == 'v':
        if expr.left in symbol_dict:
            return symbol_dict[expr.left]
        else:
            return None
    elif expr.type == 'i':
        return int(expr.left)
    else:
        left = eval_expression(expr.left, symbol_dict)
        right = eval_expression(expr.right, symbol_dict)

        if left is None or right is None:
            return None

        if expr.type == '-':
            return left - right
        elif expr.type == '+':
            return left + right
        elif expr.type == '*':
            return left * right
        elif expr.type == '>':
            return left > right
        else:
            return left == right


def evaluate_ast(node, symbol_dict):
    if isinstance(node, Assign):
        var = node.variable.left
        symbol_dict[var] = eval_expression(node.expr, symbol_dict)
    elif isinstance(node, If):
        expr_result = eval_expression(node.expr, symbol_dict)

        if expr_result is None:
            # unable to evaluate expression because symbol dictionary doesn't
            # contain enough information
            return

        if expr_result:
            if isinstance(node.then_branch, list):
                for i in node.then_branch:
                    evaluate_ast(i, symbol_dict)
            else:
                evaluate_ast(node.then_branch, symbol_dict)
        else:
            if isinstance(node.else_branch, list):
                for i in node.else_branch:
                    evaluate_ast(i, symbol_dict)
            else:
                evaluate_ast(node.else_branch, symbol_dict)
    elif isinstance(node, While):
        expr_result = eval_expression(node.expr, symbol_dict)

        if expr_result is None:
            # unable to evaluate expression because symbol dictionary doesn't
            # contain enough information
            return

        while expr_result:
            if isinstance(node.prog, list):
                for i in node.prog:
                    evaluate_ast(i, symbol_dict)
            else:
                evaluate_ast(node.prog, symbol_dict)

            expr_result = eval_expression(node.expr, symbol_dict)
    elif isinstance(node, InstructionList):
        for i in node.list:
            evaluate_ast(i, symbol_dict)


