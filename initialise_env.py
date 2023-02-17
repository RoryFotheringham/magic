from z3 import *
import synth_utils


class StatesAPI:
    def __init__(self, k, depth, instance):
        self.depth = depth
        self.state_vectors = {}
        self.state_vectors.update({0 : Array('s_{}_0'.format(instance), IntSort(), IntSort())})

        for i in range(1, k+1):
            self.state_vectors.update({i : Array('s_{}_{}'.format(instance, i), IntSort(), IntSort())})

    def get_array(self, i):
        return self.state_vectors.get(i)
    def get(self, tpl):
        i = tpl[0]
        j = tpl[1]
        
        # if j >= self.depth:
        #     print("bad news! don't call .get() with a value >= depth, remember, indeces are from 0\n." +
        #     "We are dealing with potentially infinite arrays and i have only a little laptop, thank you")
        #     raise ValueError

        return self.state_vectors.get(i)[j]
        

class Variables:
    def __init__(self, k, depth, instance):
        #self.solver = Solver()
        self.instance = instance
        self.k = k
        self.depth = depth
        self.comps = {}
        self.states = StatesAPI(k, depth, instance)
        self.selected = {}
        self.number_of_operators = 15
        self.lib_size = self.k + self.number_of_operators #  warning - must update this value if changing number of components in library
                          #  don't get lib_size confused with k. lib_size describes range of component values. 
                          # k is the length of the trick. Remember, is shorter than the number of components. 
        self.selected.update({0 : Int('aud_{}_0'.format(instance))})
        
        # for j in range(self.depth):
        #     self.states.update({(0, j) : Int("s_0_{}".format(j))})
    
        self.choices = {}

        self.generate_variables()
        self.value_range = self.constrain_values()
    
    def generate_variables(self):
        for i in range(1, self.k+1):
            self.comps.update({i : Int("i_{}".format(i))})
            self.choices.update({i : Int("c_{}_{}".format(self.instance,i))})
            self.selected.update({i : Int("aud_{}_{}".format(self.instance, i))})
            # for j in range(self.depth):
            #     self.states.update({(i,j) : Int("s_{0}_{1}".format(i, j))})        


    def constrain_values(self):
        #this function should return a formula, a satisfying assignment to which is the values of the vars being in the right range
        

        selected_vals = []
        # constrains 
        selected_vals.append(self.selected.get(0) == self.depth-1)
        for i in range(1, self.k+1):
            selected_vals.append(And([self.selected.get(i) >= 0, self.selected.get(i) < self.depth]))

        #constrain values of element in component vector
        component_vals = []
        for i in range(1, self.k+1):
            component_vals.append(And([self.comps[i] > 0, self.comps[i] <= self.lib_size]))
            for j in range(1, self.k+1):
                if i != j:
                    # for any pair of distinct component values i_m and i_n, where m != n, i_m != i_n
                    component_vals.append(self.comps.get(i) != self.comps.get(j))
            
        #constrains values of each element of each state vector to be either 1 or -1
        all_face_down = And([self.states.get((0, j)) == -1 for j in range(self.depth)])
        states_vals = []
        states_vals.append(all_face_down)
        for i in range(1, self.k+1):
            for j in range(self.depth):
                # to change this value range, add all valid values to the disjunction below
                # or just give a conjunction of range line And (> 0, < 100)
                states_vals.append(Or([self.states.get((i,j)) == 1, self.states.get((i,j)) == -1]))
                
        # constrains values of choice vector to be a valid index of one of the state vectors
        # that is: c_m >= 0 and c_m < depth for all m
        choice_vals = []
        for i in range(1, self.k+1):
            choice_vals.append(And([self.choices.get(i) >= 0, self.choices.get(i) < self.depth]))

        
            
        # conjoins these formulae into value_range
        value_range = And([And(component_vals), And(states_vals), And(choice_vals), And(selected_vals)])
        f = open('range', 'w')
        temp = Solver()
        temp.add(value_range)
        f.write(str(temp.assertions()))
        f.close()

        return value_range


class Formulae:
    def __init__(self, vars):
        self.vars = vars
        self.value_range = vars.value_range
         
        def generate_lib(moves_in_lib, move_comps_dict):
            lib = []
            for move in moves_in_lib:
                comps = move_comps_dict.get(move)
                for comp in comps:
                    lib.append(comp)
            return lib

        def generate_dicts(title_list):
            assignments = 1
            move_comps_dict = {}
            comp_move_dict = {}
            while assignments <= vars.number_of_operators:
                
                move_name = title_list[(assignments-1)%(len(title_list))]
                if move_comps_dict.get(move_name):
                    
                    #move_comps_dict.update({move_name: move_comps_dict.get(move_name).append(assignments)})
                    move_comps_dict.get(move_name).append(assignments)
                else:
                    move_comps_dict.update({move_name : [assignments]})
                comp_move_dict.update({assignments : move_name})
                assignments += 1
            return move_comps_dict, comp_move_dict
        
        move_comps_dict, comp_move_dict = generate_dicts(['top_to_bottom', 
                                                          'flip_2',
                                                          'straight_cut',
                                                          'top_2_to_bottom',
                                                          'turn_top'])
                
        self.move_comps_dict = move_comps_dict
        self.comp_move_dict = comp_move_dict
        self.nondetlib = generate_lib(['straight_cut'], move_comps_dict)
        self.subsequences = self.generate_subsequences()

    # subsequence is a list of integers
    def phi_nondet(self, subsequence):
        nondet_seq = []
        for i in subsequence:
            for nd_value in self.nondetlib:
                if i != 0:
                    nondet_seq.append(self.vars.comps.get(i) == nd_value)
        return Or(nondet_seq)

    def phi_looping(self, subsequence):
        looping = And([self.vars.states.get((subsequence[0],j)) == 
         self.vars.states.get((subsequence[-1],j)) for j in range(self.vars.depth)])
        return looping

    def generate_subsequences(self):
        sequence = list(range(self.vars.k+1))
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

        
        
    def constrain_connections(self):
 
        vars = self.vars
        valid_transitions = []

        for i in range(1, vars.k+1):

            noop_states = And([vars.states.get((i-1, j)) == vars.states.get((i, j)) for j in range(vars.depth)])
            noop_selected = And(vars.selected.get(i-1) == vars.selected.get(i))
            noop = And([noop_states, noop_selected])

            top_to_bottom_states = And([vars.states.get((i-1, j)) == 
            vars.states.get((i, (j + vars.depth-1)%vars.depth)) for j in range(vars.depth)])

            top_to_bottom_selected = And([If(vars.selected.get(i-1) == j,
             vars.selected.get(i) == (j + (vars.depth-1))%vars.depth, True) for j in range(vars.depth)])

            top_to_bottom = And([top_to_bottom_states, top_to_bottom_selected])

            flip_2_states = If(vars.states.get((i-1, 0)) == vars.states.get((i-1,1)),
             And([vars.states.get((i-1, 0)) == vars.states.get((i, 0)) * -1,
                vars.states.get((i-1, 1)) == vars.states.get((i, 1)) * -1]), noop)


            flip_2_extra_states = And([vars.states.get((i-1, j)) ==
             vars.states.get((i, j)) for j in range(2, vars.depth)])

            flip_2_selected = And([If(vars.selected.get(i-1) == 0, vars.selected.get(i) == 1, True),
            If(vars.selected.get(i-1) == 1, vars.selected.get(i) == 0, True)])

            flip_2_extra_selected = And([If(vars.selected.get(i-1) == j,
             vars.selected.get(i) == j, True) for j in range (2, vars.depth)])

            flip_2 = And([flip_2_states, flip_2_selected, flip_2_extra_selected, flip_2_extra_states])


            #we assume that a choice value 0 is a cut at the deck between the 0th card and the rest of the deck
            #0th card being the first card - the card at index 0

            straight_cut_states = And([vars.states.get((i-1,j)) ==
             vars.states.get((i,(j-vars.choices.get(i))%vars.depth)) for j in range(vars.depth)])
             
            straight_cut_selected = vars.selected.get(i-1) == ((vars.selected.get(i) +
             vars.choices.get(i))%vars.depth)

            straight_cut = And([straight_cut_states, straight_cut_selected])

            top_2_to_bottom_states = And([vars.states.get((i-1, j)) == 
            vars.states.get((i, (j + vars.depth-2)%vars.depth)) for j in range(vars.depth)])

            top_2_to_bottom_selected = And([If(vars.selected.get(i-1) == j,
             vars.selected.get(i) == (j + (vars.depth-2))%vars.depth, True) for j in range(vars.depth)])

            top_2_to_bottom = And([top_2_to_bottom_selected, top_2_to_bottom_states])

            turn_top_states = vars.states.get((i-1, 0)) == vars.states.get((i, 0))*-1 

            turn_top_extra_states = And([vars.states.get((i-1, j)) ==
             vars.states.get((i, j)) for j in range(1, vars.depth)])

            turn_top_extra_selected = vars.selected.get(i-1) == vars.selected.get(i)

            turn_top = And([turn_top_states, turn_top_extra_states, turn_top_extra_selected])

            valid_transitions.append(And([If(Or([vars.comps.get(i) == comp for comp in self.move_comps_dict.get('top_to_bottom')]), top_to_bottom, True),
            If(Or([vars.comps.get(i) == comp for comp in self.move_comps_dict.get('flip_2')]), flip_2, True),
            If(Or([vars.comps.get(i) == comp for comp in self.move_comps_dict.get('straight_cut')]), straight_cut, True),
            If(Or([vars.comps.get(i) == comp for comp in self.move_comps_dict.get('top_2_to_bottom')]), top_2_to_bottom, True), 
            If(Or([vars.comps.get(i) == comp for comp in self.move_comps_dict.get('turn_top')]), turn_top, True), 
            And([If(vars.comps.get(i) == j+vars.number_of_operators+1, noop, True)
             for j in range(vars.k)])
            ]))

            # valid_transitions.append(And([If(Or(vars.comps.get(i) == 1, vars.comps.get(i) == 2, vars.comps.get(i) == 3), top_to_bottom, True),
            # If(Or(vars.comps.get(i) == 4, vars.comps.get(i) == 5, vars.comps.get(i) == 6), flip_2, True),
            # If(Or(vars.comps.get(i) == 7, vars.comps.get(i) == 8, vars.comps.get(i) == 9), straight_cut, True),
            # If(Or(vars.comps.get(i) == 10,vars.comps.get(i) == 11, vars.comps.get(i) == 12), top_2_to_bottom, True), 
            # If(Or(vars.comps.get(i) == 13, vars.comps.get(i) == 14, vars.comps.get(i) == 15), turn_top, True), 
            # And([If(vars.comps.get(i) == j+vars.number_of_operators+1, noop, True)
            #  for j in range(vars.k)])
            # ]))
        
        return And(valid_transitions)
        

    def forbid_trivial_tricks(self):
        vars = self.vars
        cut_assertions_disjunct = []
        cut_assertions_conjunct = []
        for i in range(1, vars.k+1):
            if i > 1 and i < vars.k:   
                cut_assertions_disjunct = cut_assertions_disjunct + [vars.comps.get(i) == comp for comp in self.move_comps_dict.get('straight_cut')]
                
            if i == 1 or i == vars.k:
                cut_assertions_conjunct = cut_assertions_conjunct + [vars.comps.get(i) != comp for comp in self.move_comps_dict.get('straight_cut')]

        all_flip_moves = [] # all flip moves asserts the disjunction that a component must be a flip move
                            # over all components. This is vacuous on its own but the array can be spliced
                            # and we can constrain the range of flip moves. 
        for i in range(1, vars.k+1):
            flip_dis = Or(Or([vars.comps.get(i) == comp for comp in self.move_comps_dict.get('turn_top')]),
                           Or([vars.comps.get(i) == comp for comp in self.move_comps_dict.get('flip_2')]))
            
            all_flip_moves.append(flip_dis)
            
        
        
        flip_after_cut_list = [] # this constrains the range of flip moves conditional on the presence of
                                 # a cut move to ensure that a flip is always after a cut
        for i in range(1, vars.k+1):        
            flip_after_cut = If(Or([vars.comps.get(i) == comp for comp in self.move_comps_dict.get('straight_cut')]),
                                Or(all_flip_moves[i:]), True)
            
            flip_after_cut_list.append(flip_after_cut)
            
        with open('flip_after_cut_list.txt', 'w') as f:
            f.write(str(flip_after_cut_list))

        singular_flips = []
        for i in range(1, vars.k):
            turn_top_singular = [Implies(vars.comps.get(i) == comp, vars.comps.get(i+1) != comp) for comp in self.move_comps_dict.get('turn_top')]
            flip_2_singular = [Implies(vars.comps.get(i) == comp, vars.comps.get(i+1) != comp) for comp in self.move_comps_dict.get('flip_2')]
            singular_flips.append(And(turn_top_singular))
            singular_flips.append(And(flip_2_singular))
        #print(self.subsequences[13])
        forbid_det_loop_subseq = [Implies(self.phi_looping(q), self.phi_nondet(q)) for q in self.subsequences]
        print(forbid_det_loop_subseq[13])
        print(forbid_det_loop_subseq[14])

        #forbid_trivial_tricks = And([And(forbid_det_loop_subseq), And(cut_assertions_conjunct), Or(cut_assertions_disjunct), And(flip_after_cut_list), And(singular_flips)])
        forbid_trivial_tricks = And([And(cut_assertions_conjunct), Or(cut_assertions_disjunct), And(flip_after_cut_list), And(singular_flips)])
        
        #the det_loop_subseq is added outside the model
        
        return forbid_trivial_tricks

    def bb_hummer_states(self):
        # returns final state constraint formula for baby_hummer trick. 
        vars = self.vars
        final_state_vector = []

        for i in range(vars.depth):
            final_state_vector.append(vars.states.get((vars.k, i)))
        # if the sum of the cards is depth then they are all == 1 if the sum is two less then only one value is deviating
        # that is what we want to enforce
        only_one_odd_card = Or([Sum(final_state_vector) == vars.depth-2, Sum(final_state_vector) == -(vars.depth-2)])
        
        selected_must_be_minus = []
        selected_must_be_positive = []
        for i in range(vars.depth):
            # if the value of a card is -1 at depth i, then that depth value i but also be where the audience
            # selected card is at time point k. resp for +1
            selected_must_be_minus.append(If(final_state_vector[i] == -1, vars.selected.get(vars.k) == i, True))
            selected_must_be_positive.append(If(final_state_vector[i] == 1, vars.selected.get(vars.k) == i, True))
        selected_must_be_minus = And(selected_must_be_minus)
        selected_must_be_positive = And(selected_must_be_positive)


        odd_is_selected = And([If(Sum(final_state_vector) == vars.depth-2, selected_must_be_minus, True),
         If(Sum(final_state_vector) == -(vars.depth-2), selected_must_be_positive, True)])


        bb_hummer_states = And([odd_is_selected, only_one_odd_card])

        with open('bb_hummer_states.txt', 'w') as f:
            f.write(str(bb_hummer_states))


        return bb_hummer_states



def initialise_env(k, depth, instance):
    variables = Variables(k, depth, instance)
    formulae = Formulae(variables)
    #formulae.generate_subsequences()
    phi_spec = formulae.bb_hummer_states()

    with open('phi_spec.txt', 'w') as f:
            f.write(str(phi_spec))

    forbid_trivial = formulae.forbid_trivial_tricks()

    trans = formulae.constrain_connections()
    val_range = variables.value_range

    with open('val_range.txt','w') as f:
        f.write(str(val_range))

    with open('forbid_trivial.txt','w') as f:
        f.write(str(forbid_trivial))

    with open('trans.txt','w') as f:
        f.write(str(trans))

    phi_des = And([val_range, trans, forbid_trivial])
    #phi_des = And([val_range, trans])
    return variables, formulae, phi_des, phi_spec


def verify_test(k, depth):
    variables, formulae, phi_des, phi_spec = initialise_env(k, depth)

    trick = synth_utils.list_to_constraint(
    [7, 3, 28, 13, 16, 8, 9, 15, 4, 12, 5, 11, 14, 2, 1], variables.comps
    )

    ver = And(phi_des, Not(phi_spec))
    s = Solver()
    s.add(ver, trick)
    check = s.check()
    print(check)
    if str(check) == 'sat': 
                   
        model = s.model()
        #synth_utils.pp_counter_model(model, variables)
        
    solve = Solver()
    solve.add(And(phi_des, phi_spec), trick)
    solve.check()
    synth_utils.pp_counter_model(solve.model(),variables, formulae)

#verify_test(15, 5)


    
