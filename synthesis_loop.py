from xml.dom import InvalidStateErr
from initialise_env import initialise_env
import synth_utils
from z3 import *


def verify(instance, k, depth, candidate):
    
    ver_variables, ver_formulae, ver_phi_des, ver_phi_spec = initialise_env(k, depth, str(instance+1))
    ver = And(ver_phi_des, Not(ver_phi_spec))
    s = Solver()
    print('the candidate being passed into the verifier\n{}'.format(candidate))
    s.add(ver, candidate)
    check = s.check()
    if str(check) == 'sat':
        model = s.model()
        with open('candidate_model.txt', 'w') as f:
            f.write(str(model))
        counter_example = synth_utils.counter_example_from_model(model, ver_variables)
        return counter_example, ver_variables, ver_formulae
    else:
        return None, None, None # None should be caught signifying good trick

def synthesise(instance, k, depth, input_set, synth_list):
    
    print(input_set)
    synth_variables, synth_formulae, synth_phi_des, synth_phi_spec = initialise_env(k, depth, str(instance))
    new_synth = And(synth_phi_des, synth_phi_spec)
    synth_list.append(new_synth)
    s = Solver()
    
    if len(input_set) != len(synth_list):
        raise InvalidStateErr('there is not a corresponding synth env for each input')
    
    to_add = []
    for i in range(len(input_set)):
        synth = synth_list[i]
        choices = input_set[i]
        to_add.append(synth)
        to_add.append(choices)
        
        #s.add(synth, choices)
        
        
    s.add(And(to_add))
    with open('synth_query.txt', 'w') as f:
            f.write(str(s.sexpr()))
    check = s.check()
    if str(check) == 'unsat':
        return None, None, None
    else:
        model = s.model()
        candidate = synth_utils.candidate_from_model(model, synth_variables)
        return candidate, model, synth_list

# in order to extract the values of the component vector I need to directly query
# a satisfied model. For this, synthesiser needs to return a model which is only 
# used when the synthesis is complete and we want to return a trick. 
# for all other occasions, it is fine for it to float around as a global
# because it is a pretty lightweight object

def synth_loop(k, depth):
    '''
    this is where the magic happens
    '''
    
    # initialise the environment for the verifier which never changes
    initial_variables, initial_formulae, initial_phi_des, initial_phi_spec = initialise_env(k, depth, '0')
    ver = And(initial_phi_des, Not(initial_phi_spec))
    initial_synth = And(initial_phi_des, initial_phi_spec)

    input_set = synth_utils.init_input_set(initial_variables)
    synth_list = []
    instance = 0
    while True:
        candidate, model, synth_list = synthesise(instance, k, depth, input_set, synth_list)
        #print(candidate)
        if candidate == None: # we must explicitly check None equality 
                              # because z3 type can't cast to concrete bool
            print('synthesis failed')
            break
        counter_example, ver_variables, ver_formulae = verify(instance, k, depth, candidate)
        if counter_example == None:
            print('synthesis complete!')
            print(synth_utils.pp_counter_model(model, initial_variables, initial_formulae))
            trick_list = synth_utils.trick_from_model(model, initial_variables)
            print(trick_list)
            print(synth_utils.trick_to_strings(trick_list, initial_formulae))
            break
        else:
            input_set.append(counter_example)
            #print(counter_example)
        instance += 1

synth_loop(15, 6)