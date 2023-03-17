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

def pp_counter_model(model, variables, formulae):
    for i in range(0, variables.k+1):
        state_vector = []
        for j in range(variables.depth):
            state_vector.append(simplify(model[variables.states.get_array(i)][j]))
        print('s_{}: {}'.format(i, state_vector))
        print('aud_{}: {}'.format(i, model[variables.selected.get(i)]))
        if i > 0:
            print('comp_{}: {}'.format(i, formulae.comp_move_dict.get(model[variables.comps.get(i)].as_long())))
            print('choice_{}: {}'.format(i, model[variables.choices.get(i)]))
        print('\n')

def counter_example_from_model(model, variables):
    counter_example = []
    for i in range(1, variables.k+1):
        counter_example.append(variables.choices.get(i) == model[variables.choices.get(i)])
        #counter_example.append(variables.states.get_array(i) == model[variables.states.get_array(i)])
        #counter_example.append(variables.selected.get(i) == model[variables.selected.get(i)]) 
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

def trick_to_strings(trick_list, formulae):
    move_dict = formulae.comp_move_dict
    
    strings = []
    for move in trick_list:
        name = move_dict.get(int(move.as_long()))
        if name:
            strings.append(name)
    return strings


#def trick_from_candidate(candidate, variables, formulae):
    # for i in range(1, variables.k+1):
    #     print(candidate[0]
    #print(candidate)

def init_input_set(variables, seed=0):
    input_set = []
    for i in range(1, variables.k+1):
        if seed > 0:
            input_set.append(variables.choices.get(i) == 1)
            seed = seed -1
        else:
            input_set.append(variables.choices.get(i) == 0)
    return [And(input_set)]


# it could be interesting to see whether the explicit instantiation of the states
# makes a difference but not an essential part of the project.
#
# def phi_looping(self, subsequence):
#     looping = And([self.vars.states.get((subsequence[0],j)) == 
#         self.vars.states.get((subsequence[-1],j)) for j in range(self.vars.depth)])
#     return looping        
        
def generate_subsequences(trick_len):
        sequence = list(range(trick_len+1))
        n = len(sequence)
        subsequences = []
        for sub_len in range(2, n + 1):
            
            for i in range(n - sub_len + 1):
                subsequence = []
                j = i + sub_len -1
                for k in range(i, j+1):
                    subsequence.append(sequence[k])
                subsequences.append(subsequence)
        return subsequences
