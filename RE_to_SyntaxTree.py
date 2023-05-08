class SyntaxTreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.firstpos = set()
        self.lastpos = set()
        self.followpos = set()


def regex_to_postfix(regex):
    # Implement the Shunting Yard algorithm to convert the regular expression to postfix notation
    precedence = {'*': 3, '.': 2, '|': 1}
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
    return char in ['*', '.', '|']



def regex_to_syntax_tree(regex):
    postfix_regex = regex_to_postfix(regex)

    # Use a stack to build the syntax tree from the postfix expression
    stack = []
    for token in postfix_regex:
        if is_operator(token):
            right = stack.pop()
            left = stack.pop()
            node = SyntaxTreeNode(token)
            node.left = left
            node.right = right
            stack.append(node)
        else:
            node = SyntaxTreeNode(token)
            stack.append(node)
    syntax_tree = stack.pop()
    calculate_positions(syntax_tree)
    print_positions(syntax_tree)
    return syntax_tree


def syntax_tree_to_dfa(syntax_tree):
    # Implement Thompson's algorithm to convert the syntax tree to a DFA
    dfa = ...
    return dfa


def calculate_positions(node):
    if node is None:
        return
    calculate_positions(node.left)
    calculate_positions(node.right)
    if node.value == '|':
        node.firstpos = node.left.firstpos.union(node.right.firstpos)
        node.lastpos = node.left.lastpos.union(node.right.lastpos)
        node.followpos = node.left.followpos.union(node.right.followpos)
    elif node.value == '.':
        node.firstpos = node.left.firstpos
        if node.left.is_nullable():
            node.firstpos = node.firstpos.union(node.right.firstpos)
        node.lastpos = node.right.lastpos
        if node.right.is_nullable():
            node.lastpos = node.lastpos.union(node.left.lastpos)
        if node.right.is_nullable():
            node.followpos = node.left.followpos.union(node.right.followpos)
        else:
            node.followpos = node.right.followpos
    elif node.value == '*':
        node.firstpos = node.left.firstpos
        node.lastpos = node.left.lastpos
        node.followpos = node.left.followpos
    else:
        node.firstpos = {node}
        node.lastpos = {node}


def print_positions(node):
    if node is None:
        return
    print(f"{node.value}:")
    if node.left is None and node.right is None: #If nullable
        print(f"  First pos: {{{node.value}}}")
        print(f"  Last pos: {{{node.value}}}")
        print(f"  Follow pos: set()")
    else:
        print(f"  First pos: {node.firstpos}")
        print(f"  Last pos: {node.lastpos}")
        print(f"  Follow pos: {node.followpos}")
    print_positions(node.left)
    print_positions(node.right)


regex = "a(b|c)*"
syntax_tree = regex_to_syntax_tree(regex)
dfa = syntax_tree_to_dfa(syntax_tree)
