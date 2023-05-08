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


class SyntaxTree:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.node_type = node_type
        self.value = value
        self.left = left
        self.right = right
        self.first_pos = set()
        self.last_pos = set()
        self.follow_pos = set()

    def __str__(self):
        return f'{self.node_type}: {self.value}'


class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accepting_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accepting_states = accepting_states

    def accepts(self, string):
        current_state = self.start_state
        for char in string:
            if char not in self.alphabet:
                return False
            current_state = self.transitions[current_state][char]
        return current_state in self.accepting_states


def direct_method(regex):
    tree = parse_regex(regex)
    tree = augment_syntax_tree(tree)
    follow_pos = compute_follow_pos(tree)
    dfa = build_dfa(tree, follow_pos)
    print_first_last_pos(tree)
    print_follow_pos(follow_pos)
    return dfa


def parse_regex(regex):
    index = 0
    current_char = regex[index]

    def next_char():
        nonlocal index, current_char
        index += 1
        if index < len(regex):
            current_char = regex[index]
        else:
            current_char = None

    def parse_regex():
        term = parse_term()
        if current_char == '|':
            next_char()
            return SyntaxTree('|', left=term, right=parse_regex())
        else:
            return term

    def parse_term():
        factor = parse_factor()
        if current_char in ['(', '|', None] or current_char.isalpha():
            return SyntaxTree('concat', left=factor, right=parse_term())
        else:
            return factor

    def parse_factor():
        base = parse_base()
        if current_char == '*':
            next_char()
            return SyntaxTree('*', left=base)
        else:
            return base

    def parse_base():
        if current_char == '(':
            next_char()
            expr = parse_regex()
            if current_char != ')':
                raise ValueError('Expected closing parenthesis')
            next_char()
            return expr
        elif current_char.isalpha():
            value = current_char
            next_char()
            return SyntaxTree('symbol', value=value)
        else:
            raise ValueError('Invalid character')

    return parse_regex()


def augment_syntax_tree(tree):
    node_id = 1

    def augment_node(node):
        nonlocal node_id
        node_id += 1
        node.id = node_id
        if node.node_type == 'symbol':
            node.nullable = False
            node.first_pos = set([node.id])
            node.last_pos = set([node.id])
        elif node.node_type == 'concat':
            augment_node(node.left)
            augment_node(node.right)
            node.nullable = node.left.nullable and node.right.nullable
            if node.left.nullable:
                node.first_pos = node.left.first_pos.union(node.right.first_pos)
            else:
                node.first_pos = node.left.first_pos
            if node.right.nullable:
                node.last_pos = node.left.last_pos.union(node.right.last_pos)
            else:
                node.last_pos = node.right.last_pos
        elif node.node_type == '|':
            augment_node(node.left)
            augment_node(node.right)
            node.nullable = node.left.nullable or node.right.nullable
            node.first_pos = node.left.first_pos.union(node.right.first_pos)
            node.last_pos = node.left.last_pos.union(node.right.last_pos)
        elif node.node_type == '*':
            augment_node(node.left)
            node.nullable = True
            node.first_pos = node.left.first_pos
            node.last_pos = node.left.last_pos
        else:
            raise ValueError('Invalid node type')

        augment_node(tree)
        return tree

        def compute_follow_pos(tree):
            follow_pos = {node_id: set() for node_id in range(1, tree.id + 1)}


        def traverse_tree(node):
            if node.node_type == 'concat':
                for id in node.left.last_pos:
                    follow_pos[id].update(node.right.first_pos)
            elif node.node_type == '*':
                for id in node.last_pos:
                    follow_pos[id].update(node.first_pos)
            if node.left:
                traverse_tree(node.left)
            if node.right:
                traverse_tree(node.right)

        traverse_tree(tree)
        return follow_pos

        def build_dfa(tree, follow_pos):
            start_state = frozenset([tree.first_pos.pop()])

        states = set()
        alphabet = set()
        transitions = {}


        def get_state(nodes):
            state = frozenset(nodes)
            if state not in states:
                states.add(state)
                transitions[state] = {}
                for symbol in alphabet:
                    transitions[state][symbol] = frozenset(
                        {follow_pos[n] for n in nodes if n.value == symbol}
                    )
            return state

        def traverse_tree(node):
            if node.node_type == 'symbol':
                alphabet.add(node.value)
                node.dfa_nodes = set([node])
            elif node.node_type == 'concat':
                traverse_tree(node.left)
                traverse_tree(node.right)
                node.dfa_nodes = node.left.dfa_nodes.union(node.right.dfa_nodes)
            elif node.node_type == '|':
                traverse_tree(node.left)
                traverse_tree(node.right)
                node.dfa_nodes = node.left.dfa_nodes.union(node.right.dfa_nodes)
            elif node.node_type == '*':
                traverse_tree(node.left)
                node.dfa_nodes = node.left.dfa_nodes
            else:
                raise ValueError('Invalid node type')

        traverse_tree(tree)

        start_state = get_state(tree.first_pos)

        accepting_states = set()
        for state in states:
            if any(node.id in state and node.node_type == 'symbol' for node in state):
                accepting_states.add(state)

        return DFA(states, alphabet, transitions, start_state, accepting_states)

        def print_first_last_pos(tree):
            print('First pos:')

        for node in sorted(tree.dfa_nodes, key=lambda n: n.id):
            print(f'{node.value}: {node.first_pos}')
        print('\nLast pos:')
        for node in sorted(tree.dfa_nodes, key=lambda n: n.id):
            print(f'{node.value}: {node.last_pos}')
        print()

        def print_follow_pos(follow_pos):
            print('Follow pos:')

        for node_id in sorted(follow_pos.keys()):
            print(f'{node_id}: {follow_pos[node_id]}')
        print()