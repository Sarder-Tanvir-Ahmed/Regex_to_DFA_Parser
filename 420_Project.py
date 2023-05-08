# This Project is made by (19101153) Sarder Tanvir Ahmed
# and (19101368) Abrar Ahsan Efaz
#
# RE 1 : [+/%*-]|==|!=|<=|>=|[<>]=
# Function : This programming regex matches arithmetic operators
# Example Code Block : '''
# x = 10
# y = 20
# if x < y:
#     z = x + y
# else:
#     z = x - y
# '''
#
# RE 2 : (and|!=|\|\||&&|not|!)
# Function : This programming regex matches logical operators.
# Example code_block = '''
#  if (condition1 && condition2 || !condition3) {
#   // do something
# } else if (condition1 != condition2) {
#   // do something else
# }
#  '''

import re



class Node:
    def __init__(self, token=None, left=None, right=None):
        self.token = token
        self.left = left
        self.right = right
        self.position = None
        self.is_nullable = False

    def set_position(self, position):
        self.position = position

    def compute_nullable(self):
        if self.token in ['epsilon', 'empty']:
            self.is_nullable = True

    def __str__(self):
        return str(self.token)


#  ---------------------------------------------------------

class State:
    def __init__(self):
        self.states = set()
        self.transitions = {}
        self.start_state = None
        self.accept_states = set()

    def add_state(self, state):
        self.states.add(state)
        self.transitions[state] = {}

    def add_transition(self, start_state, symbol, end_state):
        self.transitions[start_state][symbol] = end_state

    def set_start_state(self, state):
        self.start_state = state

    def add_accept_state(self, state):
        self.accept_states.add(state)


#  --------------------------------------------------------

def regex_to_postfix(regex):
    precedence = {
        '(': 0, ')': 0,
        '[': 0, ']': 0,
        '{': 0, '}': 0,
        '<': 4, '>': 4, '<=': 4, '>=': 4, '==': 4, '!=': 4,
        '*': 7, '/': 7, '%': 7,
        '+': 5, '-': 5,
        '=': 6, '-=': 6, '=<': 6, '=>': 6, '+=': 6,
        '|': 3, '^': 2, '&': 1,
        '||': 1, '&&': 2, '!': 3,
    }
    tokens = re.findall(r'\(|\)|[+/*%]|\-=?|==|!=|<=|>=|[<>]=?|=\+?|&&|\|\||!|\w+', regex)
    output = []
    opstack = []
    for token in tokens:
        if re.match(r'\w+', token):
            output.append(token)
        else:
            if token == '(':
                opstack.append(token)
            elif token == ')':
                while opstack[-1] != '(':
                    output.append(opstack.pop())
                opstack.pop()
            else:
                while opstack and opstack[-1] != '(' and precedence[opstack[-1]] >= precedence[token]:
                    output.append(opstack.pop())
                opstack.append(token)
    while opstack:
        output.append(opstack.pop())
    return output


def is_operator(char):
    return char in ['*', '.', '|'] and char != ''


def postfix_to_syntax_tree(postfix_expr):
    stack = []
    position = 1
    for token in postfix_expr:
        node = Node(token=token)
        node.set_position(position)
        position += 1
        stack.append(node)
        while len(stack) > 1:
            right = stack.pop()
            left = stack.pop()
            node = Node(token='concat', left=left, right=right)
            node.set_position(position)
            position += 1
            stack.append(node)
    root = stack.pop()
    root.set_position(0)
    return root


def print_syntax_tree(node, depth=0, is_left=None):
    if node is None:
        return

    # Print the node's position, token, and left and right child positions
    if is_left:
        prefix = "├─L─"
    elif is_left is False:
        prefix = "├─R─"
    else:
        prefix = "───"
    print(" " * depth + prefix + str(node.position) + ":" + str(node.token) + " (L: {}, R: {})".format(
        node.left.position if node.left else None, node.right.position if node.right else None))

    # Print the left child
    print_syntax_tree(node.left, depth + 2, True)

    # Print the right child
    print_syntax_tree(node.right, depth + 2, False)


def syntax_tree_to_dfa(root):
    dfa = State()

    # Visit each node in the syntax tree and add the corresponding states and transitions to the DFA
    def visit(node):
        if not node:
            return frozenset()

        if node.token == 'concat':
            left = visit(node.left)
            right = visit(node.right)
            return left.union(right) if left and right else frozenset()
        elif node.token == 'or':
            left = visit(node.left)
            right = visit(node.right)
            state = frozenset([node.position])
            dfa.add_state(state)
            for lstate in left:
                dfa.add_transition(state, 'epsilon', lstate)
            for rstate in right:
                dfa.add_transition(state, 'epsilon', rstate)
            return state
        elif node.token == 'kleene':
            child = visit(node.left)
            state = frozenset([node.position])
            dfa.add_state(state)
            for cstate in child:
                dfa.add_transition(cstate, 'epsilon', state)
                dfa.add_transition(state, 'epsilon', cstate)
            dfa.add_accept_state(state)  # Change: Make the kleene state an accept state
            return state
        elif node.token == 'leaf':
            state = frozenset([node.position])
            dfa.add_state(state)
            return state
        else:
            state = frozenset([node.position])
            dfa.add_state(state)
            dfa.add_transition(state, node.token, state)
            dfa.add_accept_state(state)  # Change: Make the token state an accept state
            return state

    # Create the DFA by visiting the root node
    start_state = visit(root)
    dfa.set_start_state(start_state)

    return dfa


def transitions_to_list(transitions):
    transition_list = []
    for state, transitions_from_state in transitions.items():
        for transition_symbol in transitions_from_state:
            transition_list.append(transition_symbol)
    return transition_list


def get_accepted_tokens(token_list, transition_list):
    matches = []
    for token in token_list:
        if token in transition_list:
            matches.append(token)
    return matches


code_block_1 = '''
x = 10
y = 20
if x < y:
    z = x + y
else:
    z = x - y
'''

code_block_2 = '''
 if (condition1 && condition2 || !condition3) {
  // do something
} else if (condition1 != condition2) {
  // do something else
}
 '''

print("#  ----------------------------------------- RE 1 Execution")

regex_1 = r'[/+%*-]|==|<=|>=|[<>]='
pregex_1 = regex_to_postfix(regex_1)  # + - * / % == < > <= >= = += -=
print("Post Fix Expression : ")

print(pregex_1)
syntax_tree_1 = postfix_to_syntax_tree(pregex_1)

# print("Syntax Tree : ")
# print_syntax_tree(syntax_tree_1)

Dfa = syntax_tree_to_dfa(syntax_tree_1)

# print("DFA States: ", Dfa.states)
# print("DFA Transitions: ", Dfa.transitions)
# print("DFA Start State: ", Dfa.start_state)
# print("DFA Accept States: ", Dfa.accept_states)


# Tokenize code block

tokens = re.findall(r'\b\w+\b|[+\-*/%=(),<>]+', code_block_1)
print("Tokenized Code Block 1 : ")
print(tokens)

transition_list = transitions_to_list(Dfa.transitions)
print("Transistion List for regex 1 : ")
print(transition_list)

# Run tokens through DFA
#
accepted_tokens = get_accepted_tokens(tokens, transition_list)
print("Accepted Tokens for regex 1: ")
print(accepted_tokens)

print("#  ----------------------------------------- RE 2 Execution")

regex_2 = r'(and|!=|\|\||&&|not|!)'
pregex_2 = regex_to_postfix(regex_2)  #  and != not && || !
print("Post Fix Expression : ")
print(pregex_2)
syntax_tree_2 = postfix_to_syntax_tree(pregex_2)
# print("Syntax Tree : ")
# print_syntax_tree(syntax_tree_2)
Dfa_2 = syntax_tree_to_dfa(syntax_tree_2)
# print("DFA States: ", Dfa.states)
# print("DFA Transitions: ", Dfa.transitions)
# print("DFA Start State: ", Dfa.start_state)
# print("DFA Accept States: ", Dfa.accept_states)

# Tokenize code block

tokens_2 = re.findall(r'\b\w+\b|[+\-*/%=!(),<>]+|\|\||&&', code_block_2)

print("Tokenized Code Block 2 : ")
print(tokens_2)

transition_list_2 = transitions_to_list(Dfa_2.transitions)
print("Transistion List for regex 2 : ")
print(transition_list_2)

# Run tokens through DFA
#
accepted_tokens_2 = get_accepted_tokens(tokens_2, transition_list_2)
print("Accepted Tokens for regex 2 : ")
print(accepted_tokens_2)
