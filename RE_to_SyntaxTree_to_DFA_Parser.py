# This Project is made by (19101153) Sarder Tanvir Ahmed
# and (19101368) Abrar Ahsan Efaz
#
# RE 1 : '\+|\-|\*|\/|\%|\=\=|\!\=|\<|\>|\<\=|\>\=|\=|\+=|\-=|and|or|not'
# Function : This is a python mathematical and logical operator regex
# that matches common operators shown above.
# Example Code Block : '''
# x = 10
# y = 20
# if x < y:
#     z = x + y
# else:
#     z = x - y
# '''
#
# RE 2 : '-?\d+(\.\d+)?([eE][+-]?\d+)?'
# Function :This regex is used to match scientific notation-based numerical values.It supports both positive
# and negative exponents, integer and floating-point integers.
# Example Code Block : '''
# x = 10
# y = -3.14
# z = 2.5e+7
# w = 'hello world'
# print(x, y, z, w)
# '''


class SyntaxTreeNode:
    def __init__(self, value, lexeme='', is_operator=False):
        # Initialize the properties of the SyntaxTreeNode object
        self.value = value
        self.left = None
        self.right = None
        self.firstpos = set()
        self.lastpos = set()
        self.followpos = set()
        self.lexeme = lexeme
        self.is_operator = is_operator
        self.position = None

    def set_position(self, position):
        # Set the position of the SyntaxTreeNode object
        self.position = position

    def is_nullable(self):
        # Determine if the SyntaxTreeNode object is nullable
        if self.is_operator:
            if self.value == '|':
                # If the operator is '|', return True if either the left or right node is nullable
                return self.left.is_nullable() or self.right.is_nullable()
            elif self.value == '.':
                # If the operator is '.', return True if both the left and right nodes are nullable
                return self.left.is_nullable() and self.right.is_nullable()
            elif self.value == '*':
                # If the operator is '*', return True
                return True
        else:
            # If the node is a leaf, return False
            return False


def regex_to_postfix(regex):
    # Implement the Shunting Yard algorithm to convert the regular expression to postfix notation
    precedence = {'*': 3, '.': 2, '|': 1, '+': 2, '-': 2, '/': 2, '%': 2, '==': 1, '!=': 1, '<=': 1, '>=': 1, '<': 1, '>': 1, '=': 1, '+=': 1, '-=': 1, 'and': 1, 'or': 1, 'not': 1, '[': 0, ']': 0, '-': 2}

    output = []
    operator_stack = []
    for char in regex:
        if char.isalnum():
            output.append(char)
        elif char == '(':
            operator_stack.append(char)
        elif char == ')':
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            if operator_stack and operator_stack[-1] == '(':
                operator_stack.pop()
        else:
            while operator_stack and operator_stack[-1] != '(' and precedence[char] <= precedence[operator_stack[-1]]:
                output.append(operator_stack.pop())
            operator_stack.append(char)
    while operator_stack:
        output.append(operator_stack.pop())
    return output


def is_operator(char):
    return char in ['*', '.', '|'] and char != ''


def regex_to_syntax_tree(regex):
    # Use a dictionary to store the position of each lexeme
    positions = {}
    for i, char in enumerate(regex):
        if not is_operator(char):
            positions[char] = i + 1

    postfix_regex = regex_to_postfix(regex)

    # Use a stack to build the syntax tree from the postfix expression
    stack = []
    for token in postfix_regex:
        if is_operator(token):
            right = stack.pop()
            left = stack.pop()
            node = SyntaxTreeNode(token, is_operator=True)
            node.left = left
            node.right = right
            stack.append(node)
        else:
            # Pass the position of the lexeme to the SyntaxTreeNode constructor
            node = SyntaxTreeNode(token, token, is_operator=False)
            node.position = positions[token]
            stack.append(node)

    syntax_tree = stack.pop()
    return syntax_tree


def syntax_tree_to_dfa(syntax_tree):
    # Implement Thompson's algorithm to convert the syntax tree to a DFA

    # Define a function to generate a new state in the DFA
    def new_state():
        nonlocal state_count
        state_count += 1
        return state_count

    # Define a function to add a transition to the DFA
    def add_transition(from_state, to_state, symbol):
        if symbol not in transitions[from_state]:
            transitions[from_state][symbol] = set()
        transitions[from_state][symbol].add(to_state)

    # Define a function to follow the nullable, firstpos, lastpos, and followpos rules
    def follow(node):
        nonlocal state, position_map

        if node.is_operator:
            if node.value == '|':
                follow(node.left)
                follow(node.right)
                for pos in node.left.lastpos:
                    add_transition(pos, state, None)
                for pos in node.right.lastpos:
                    add_transition(pos, state, None)
                for pos in node.left.firstpos:
                    position_map[pos].add(node)
                for pos in node.right.firstpos:
                    position_map[pos].add(node)
            elif node.value == '.':
                follow(node.left)
                follow(node.right)
                for pos in node.left.lastpos:
                    position_map[pos].add(node.right)
                for pos in node.right.firstpos:
                    position_map[pos].add(node.left)
            elif node.value == '*':
                follow(node.left)
                for pos in node.left.lastpos:
                    add_transition(pos, state, None)
                for pos in node.left.firstpos:
                    position_map[pos].add(node.left)
                    add_transition(pos, state, None)
                    for followpos_pos in node.left.followpos:
                        add_transition(pos, followpos_pos, None)
        else:
            position_map[node.position].add(node)
            if node.position == 1:
                add_transition(0, state, None)
            if node.is_nullable():
                for pos in node.firstpos:
                    add_transition(pos, node.position, None)
                    for followpos_node in position_map[pos]:
                        add_transition(followpos_node.position, node.position, None)

    # Initialize the state count and the DFA transitions
    state_count = 0
    transitions = [{} for i in range(100)]
    state = new_state()

    # Initialize the position map and follow the syntax tree
    position_map = {i: set() for i in range(len(syntax_tree.lexeme) + 1)}
    follow(syntax_tree)

    # Return the DFA
    return transitions


# Example code block
code_block = '''
x = 10
y = 20
if x < y:
    z = x + y
else:
    z = x - y
'''

regex = r'[+/*%]|\-|==|!=|<=|>=|[<>]=?|=\+?|-=?|'
pregex = regex_to_postfix(regex)  # + - * / % == != < > <= >= = += -= and or not
syntax_tree = regex_to_syntax_tree(pregex)
dfa = syntax_tree_to_dfa(syntax_tree)

