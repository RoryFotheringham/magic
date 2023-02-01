from initialise_env import initialise_env
import synth_utils
from z3 import *


def verify(variables, phi_des, phi_spec, candidate):
    ver = And(phi_des, Not(phi_spec))
    s = Solver()
    s.add(ver, candidate)
    check = s.check()
    if str(check) == 'sat':
        model = s.model()
        counter_example = synth_utils.counter_example_from_model(model, variables)
        return counter_example
    else:
        return None # None should be caught signifying good trick

def synthesise(variables, phi_des, phi_spec, input_set):
    synth = And(phi_des, phi_spec)
    s = Solver()
    s.add(synth, Or(input_set))
    check = s.check()
    if str(check) == 'unsat':
        return None
    else:
        model = s.model()
        candidate = synth_utils.candidate_from_model(model, variables)
        return candidate, model

# in order to extract the values of the component vector I need to directly query
# a satisfied model. For this, synthesiser needs to return a model which is only 
# used when the synthesis is complete and we want to return a trick. 
# for all other occasions, it is fine for it to float around as a global
# because it is a pretty lightweight object

def synth_loop(k, depth):
    variables, formulae, phi_des, phi_spec = initialise_env(k, depth)

    input_set = synth_utils.init_input_set(variables)
    while True:
        candidate, model = synthesise(variables, phi_des, phi_spec, input_set)
        print(candidate)
        if candidate == None: # we must explicitly check None equality 
                              # because z3 type can't cast to concrete bool
            print('synthesis failed')
            break
        counter_example = verify(variables, phi_des, phi_spec, candidate)
        if counter_example == None:
            print('synthesis complete!')
            print(synth_utils.pp_counter_model(model, variables))
            trick_list = synth_utils.trick_from_model(model, variables)
            print(trick_list)
            print(synth_utils.trick_to_strings(trick_list, formulae))
            break
        else:
            input_set.append(counter_example)

synth_loop(15, 5)