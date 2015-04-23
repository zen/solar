from __future__ import unicode_literals, print_function

import pypeg2
import re


"""
# resources
r1 = Resource(<name>, <template-path>, <destination-path>, <args>)
r2 = Resource(<name>, <template-path>, <destination-path>, <args>)

# connections
r1.ip -> r2.servers

# actions
r1:run >> r2:run
"""


class Instruction(str):
    grammar = pypeg2.word, "\n"


class Variable(pypeg2.List):
    grammar = pypeg2.word, ".", pypeg2.word


class Connection(pypeg2.List):
    grammar = Variable, pypeg2.some("->", Variable)


class ActionOperator(pypeg2.Symbol):
    regex = re.compile(r'(>>|\|)')


class Action(pypeg2.List):
    grammar = pypeg2.word, ":", pypeg2.word


class ActionExpression(pypeg2.List):
    pass


ActionExpression.grammar = [
    Action,
    ('(', ActionExpression, ')'),
], pypeg2.maybe_some(ActionOperator, ActionExpression)


def show_action_expression(e):
    if isinstance(e, ActionExpression):
        if len(e) == 1:
            show_action_expression(e[0])
        else:
            action, operator, exp = e
            print(action, operator)
            print('(')
            show_action_expression(exp)
            print(')')
    else:
        print(e)


if __name__ == '__main__':
    c = pypeg2.parse("r1.ip -> r2.servers -> r3.configs", Connection)
    c = pypeg2.parse("r1:run >> (r2:run | r3:run)", ActionExpression)

    print(c)

    if isinstance(c, Connection):
        for i in range(len(c) - 1):
            r1 = c[i]
            r2 = c[i + 1]
            print('Connect {} -> {}'.format(r1, r2))
    elif isinstance(c, ActionExpression):
        show_action_expression(c)
