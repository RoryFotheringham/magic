from z3 import *

def list_to_constraint(lst, dict):

    if len(lst) != len(dict):
        print(lst)
        print(dict)
        print('list of value incorrect length')
        raise ValueError

    constraint = []
    for i in range(1, len(lst)+1):
        var = dict[i]
        val = lst[i-1]
        constraint.append(var == val)

    return And(constraint)

def pp_model(model, variables):
    for i in range(0, variables.k+1):
        state_vector = []
        for j in range(variables.depth):
            state_vector.append(simplify(model[variables.states.get_array(i)][j]))
        print('s_{}: {}'.format(i, state_vector))
        print('aud_{}: {}'.format(i, model[variables.selected.get(i)]))
        if i > 0:
            print('comp_{}: {}'.format(i, model[variables.comps.get(i)]))
            print('choice_{}: {}'.format(i, model[variables.choices.get(i)]))
        print('\n')
            
