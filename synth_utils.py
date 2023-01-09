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

def pp_counter_model(model, variables):
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

def counter_example_from_model(model, variables):
    counter_example = []
    for i in range(1, variables.k+1):
        counter_example.append(variables.choices.get(i) == model[variables.choices.get(i)])
        counter_example.append(variables.states.get_array(i) == model[variables.states.get_array(i)])
        counter_example.append(variables.selected.get(i) == model[variables.selected.get(i)]) 
    return And(counter_example)
        
def candidate_from_model(model, variables):
    # extracts the connections into constraints
    candidate = []
    for i in range(1, variables.k+1):
        candidate.append(variables.comps.get(i) == model[variables.comps.get(i)])
    return And(candidate)

def trick_from_model(model, variables):
    trick = []
    for i in range(1, variables.k+1):
        trick.append(model[variables.comps.get(i)])
    return trick

def trick_from_candidate(candidate, variables):
    print(candidate)

def init_input_set(variables):
    input_set = []
    for i in range(1, variables.k+1):
        input_set.append(variables.choices.get(i) == 0)
    return [And(input_set)]