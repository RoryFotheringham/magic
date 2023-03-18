from xml.dom import InvalidStateErr
from initialise_env import initialise_env
import synth_utils
from initialise_env import Variables, Formulae
from z3 import *
import sys
from time import time

def phi_ndl(vars: Variables, form: Formulae, q):
    '''creates a logical formula which is true if the 
    subsequence q is not a deterministic loop
    :param q: list of integers representing subsequence of trick'''
    
    return Implies(phi_looping(vars, q), phi_nondet(vars, form, q))


def phi_looping(vars: Variables, q):
    return And([vars.states.get(((q[0]-1), j)) == vars.states.get((q[-1], j)) for j in range(vars.depth)])
  

def phi_nondet(vars: Variables, form: Formulae, q):
    nondet_disjunction = []
    for count, index in enumerate(q):
        if index != 0:
        #if count > 0:
            for nondet_comp in form.nondetlib:
                nondet_disjunction.append(vars.comps.get(index) == nondet_comp)
    return Or(nondet_disjunction)

def init_ndl_conjunction(init_vars, init_form, subseqs):
    ndl_conjunction = []
    for q in subseqs:
        ndl_disjunction = [phi_ndl(init_vars, init_form, q)]
        ndl_conjunction.append(ndl_disjunction)
    return ndl_conjunction

def append_ndl_conjunction(ndl_conjunction, new_vars, new_form, subseqs):
    if len(ndl_conjunction) != len(subseqs):
        print('ndl_conjunct should have as many elems as subsequences')
        raise InvalidStateErr 
        
    for i in range(len(ndl_conjunction)):
        q = subseqs[i]
        dis = ndl_conjunction[i]
        dis.append(phi_ndl(new_vars, new_form, q))


def verify(instance, k, depth, candidate):
    
    ver_variables, ver_formulae, ver_phi_des, ver_phi_spec = initialise_env(k, depth, str(instance+1))
    ver = And(ver_phi_des, Not(ver_phi_spec))
    s = Solver()
    #print('the candidate being passed into the verifier\n{}'.format(candidate))
    s.add(ver, candidate)
    check = s.check()
    if str(check) == 'sat':
        model = s.model()
        # with open('candidate_model.txt', 'w') as f:
        #     f.write(str(model))
        counter_example = synth_utils.counter_example_from_model(model, ver_variables)
        return counter_example, ver_variables, ver_formulae
    else:
        return None, None, None # None should be caught signifying good trick
    

def synthesise(instance, k, depth, input_set, synth_list, ndl_conjunction, subseqs):
    #print(input_set)
    print('instance ', instance)
    synth_variables, synth_formulae, synth_phi_des, synth_phi_spec = initialise_env(k, depth, str(instance))
    new_synth = And(synth_phi_des, synth_phi_spec)
    
    # in place function appends the new ndl constraints to the list for each variable
    append_ndl_conjunction(ndl_conjunction, synth_variables, synth_formulae, subseqs)
    synth_list.append(new_synth)
    
    s = Solver()
    
    if len(input_set) != len(synth_list):
        raise InvalidStateErr('there is not a corresponding synth env for each input')
    
    # for i in range(len(input_set)):
    #     synth = synth_list[i]
    #     choices = input_set[i]
    #     s.add(synth, choices)
    
    # for ndl_disjunction in ndl_conjunction:
    #     s.add(Or(ndl_disjunction))
    psi_synth = []
    for i in range(len(input_set)):
        synth = synth_list[i]
        choices = input_set[i]
        psi_synth.append(And(synth, choices))
        
    ndl_synth = []
    for ndl_disjunction in ndl_conjunction:
        ndl_synth.append(Or(ndl_disjunction))
        
    final_synth = And(And(psi_synth), And(ndl_synth))
        
    with open('final_synth.txt', 'w') as f:
        f.write(str(final_synth.sexpr()))
        
    s.add(final_synth)
        
    #for q in subseqs:
    
    # with open('synth_query.txt', 'w') as f:
    #         f.write(str(s.sexpr()))
    check = s.check()
    if str(check) == 'unsat':
        return None, None, None, None
    else:
        model = s.model()
        candidate = synth_utils.candidate_from_model(model, synth_variables)
        return candidate, model, synth_list, ndl_conjunction

# in order to extract the values of the component vector I need to directly query
# a satisfied model. For this, synthesiser needs to return a model which is only 
# used when the synthesis is complete and we want to return a trick. 
# for all other occasions, it is fine for it to float around as a global
# because it is a pretty lightweight object

def synth_loop(k, depth, seed=0):
    '''
    this is where the magic happens
    '''
    subseqs = synth_utils.generate_subsequences(k)

    # initialise the environment for the verifier which never changes
    initial_variables, initial_formulae, initial_phi_des, initial_phi_spec = initialise_env(k, depth, '0')
    
    input_set = synth_utils.init_input_set(initial_variables, seed)
    ndl_conjunction = init_ndl_conjunction(initial_variables, initial_formulae, subseqs)
    synth_list = []
    instance = 0
    while True:
        candidate, model, synth_list, ndl_conjunction = synthesise(instance, k, depth, input_set, synth_list, ndl_conjunction, subseqs)
        #print(candidate)

        if candidate == None: # we must explicitly check None equality 
                              # because z3 type can't cast to concrete bool
            #print('synthesis failed')
            final_string = 'synthesis failed'
            break
        counter_example, ver_variables, ver_formulae = verify(instance, k, depth, candidate)
        if counter_example == None:
            #print('synthesis complete!')
            #print(synth_utils.pp_counter_model(model, initial_variables, initial_formulae))
            trick_list = synth_utils.trick_from_model(model, initial_variables)
            #print(trick_list)
            #print(synth_utils.trick_to_strings(trick_list, initial_formulae))
            final_string = synth_utils.trick_to_strings(trick_list, initial_formulae)
            
            tmp = []
            for dis in ndl_conjunction:
                tmp.append(Or(dis))

            with open('ndlconj.txt', 'w') as f:
                f.write(str(ndl_conjunction))
            break
        else:
            input_set.append(counter_example)
            #print(counter_example)
        instance += 1
    #print(input_set)
    return final_string


if __name__ == '__main__':
    k = int(sys.argv[1])
    depth = int(sys.argv[2])
    seed = int(sys.argv[3])
    start = time()
    print(synth_loop(k, depth, seed))
    end = time()
    print(f'runtime: {end-start}')
