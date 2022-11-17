from z3 import *

def list_to_constraint(lst, dict):

    if len(lst) != len(dict):
        print('list of value incorrect length')
        raise ValueError

    constraint = []
    for i in range(1, len(lst)-1):
        var = dict[i]
        val = lst[i-1]
        constraint.append(var == val)

    return And(constraint)
