from z3 import *
import synth_utils

class Variables:
    def __init__(self, k, depth):
        #self.solver = Solver()
        self.k = k
        self.depth = depth
        self.comps = {}
        self.states = {}
        self.selected = {}
        self.number_of_operators = 15
        self.lib_size = self.k + self.number_of_operators #  warning - must update this value if changing number of components in library
                          #  don't get lib_size confused with k. lib_size describes range of component values. 
                          # k is the length of the trick. Remember, is shorter than the number of components. 
        self.selected.update({0 : Int('aud_0')})
        
        for j in range(self.depth):
            self.states.update({(0, j) : Int("s_0_{}".format(j))})
    
        self.choices = {}

        self.generate_variables()
        self.value_range = self.constrain_values()
    
    def generate_variables(self):
        for i in range(1, self.k+1):
            self.comps.update({i : Int("i_{}".format(i))})
            self.choices.update({i : Int("c_{}".format(i))})
            self.selected.update({i : Int("aud_{}".format(i))})
            for j in range(self.depth):
                self.states.update({(i,j) : Int("s_{0}_{1}".format(i, j))})


    def constrain_values(self):
        #this function should return a formula, a satisfying assignment to which is the values of the vars being in the right range
        
        selected_vals = []
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
        states_vals = []
        for i in range(1, self.k+1):
            for j in range(self.depth):
                # to change this value range, add all valid values to the disjunction below
                # or just give a conjunction of range line And (> 0, < 100)
                states_vals.append(Or([self.states.get((i,j)) == 1, self.states.get((i,j)) == -1]))
                
        # constrains values of choice vector to be a valid index of one of the state vectors
        # that is: c_m >= 0 and c_m < depth for all m
        choice_vals = []
        for i in range(1, self.k+1):
            choice_vals.append(And([self.choices.get(i) <= 0, self.choices.get(i) < self.depth]))
            
        # conjoins these formulae into value_range
        value_range = And([And(component_vals), And(states_vals), And(choice_vals), And(selected_vals)])
        return value_range


class Formulae:
    def __init__(self, vars):
        self.vars = vars
        self.value_range = vars.value_range

    def constrain_connections(self):
        # todo 
        # on a day that i feel good, refactor this so each component has a method
        #  that takes i and returns the variable constraining the respective component
        # this will be really useful when I start to write for other trick types.
        vars = self.vars
        valid_transitions = []

        for i in range(1, vars.k+1):
            top_to_bottom_states = And([vars.states.get((i-1, j)) == 
            vars.states.get((i, (j + vars.depth-1)%vars.depth)) for j in range(vars.depth)])

            top_to_bottom_selected = And([If(vars.selected.get(i-1) == j,
             vars.selected.get(i) == (j + (vars.depth-1))%vars.depth, True) for j in range(vars.depth)])

            top_to_bottom = And([top_to_bottom_states, top_to_bottom_selected])

            flip_2_states = And([vars.states.get((i-1, 0)) == vars.states.get((i, 0)) * -1,
                vars.states.get((i-1, 1)) == vars.states.get((i, 1)) * -1])

            flip_2_selected = And([If(vars.selected.get(i-1) == 0, vars.selected.get(i) == 1, True),
            If(vars.selected.get(i-1) == 1, vars.selected.get(i) == 0, True)])

            flip_2 = And([flip_2_states, flip_2_selected])

            #we assume that a choice value 0 is a cut at the deck between the 0th card and the rest of the deck
            #0th card being the first card - the card at index 0

            #for some reason this evals to And([False, False, False, False])
            straight_cut_states = And([vars.states.get((i-1,j)) ==
             vars.states.get((i,(j+vars.choices.get(i))%vars.depth)) for j in range(vars.depth)]) ## IMPLEMENT STATES AS ARRAY
             
            straight_cut_selected = vars.selected.get(i-1) == ((vars.selected.get(i) +
             vars.choices.get(i))%vars.depth)

            straight_cut = And([straight_cut_states, straight_cut_selected])

            top_2_to_bottom_states = And([vars.states.get((i-1, j)) == 
            vars.states.get((i, (j + vars.depth-2)%vars.depth)) for j in range(vars.depth)])

            top_2_to_bottom_selected = And([If(vars.selected.get(i-1) == j,
             vars.selected.get(i) == (j + (vars.depth-2))%vars.depth, True) for j in range(vars.depth)])

            top_2_to_bottom = And([top_2_to_bottom_selected, top_2_to_bottom_states])

            turn_top = vars.states.get(i-1, 0) == vars.states.get(i, 0)*-1 # for some reason always evals true

            noop = And([vars.states.get(i-1, j) == vars.states.get(i, j) for j in range(vars.depth)])

            valid_transitions.append(And([If(Or(vars.comps.get(i) == 1, vars.comps.get(i) == 2, vars.comps.get(i) == 3), top_to_bottom, True),
            If(Or(vars.comps.get(i) == 4, vars.comps.get(i) == 5, vars.comps.get(i) == 6), flip_2, True),
            If(Or(vars.comps.get(i) == 7, vars.comps.get(i) == 8, vars.comps.get(i) == 9), straight_cut, True),
            If(Or(vars.comps.get(i) == 10,vars.comps.get(i) == 11, vars.comps.get(i) == 12), top_2_to_bottom, True), 
            If(Or(vars.comps.get(i) == 13, vars.comps.get(i) == 14, vars.comps.get(i) == 15), turn_top, True), 
            And([If(vars.comps.get(i) == j+vars.number_of_operators+1, noop, True)
             for j in range(vars.k)])
            ]))
            if i == 2:
                slip = Solver()
                slip.add(valid_transitions)
                f = open('trans.txt', 'w')
                f.write(str(slip))
                f.close()


        return And(valid_transitions)

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
         If(Sum(final_state_vector) == -(vars.depth+2), selected_must_be_positive, True)])

        bb_hummer_states = And([odd_is_selected, only_one_odd_card])

        return bb_hummer_states


variables = Variables(12, 4)
formulae = Formulae(variables)
val_range = variables.value_range

spec = formulae.bb_hummer_states()
trans = formulae.constrain_connections()

phi_des = And([val_range, trans])
ver = Not(Implies(phi_des, spec))

original_baby = synth_utils.list_to_constraint(
    [1, 13, 7, 4, 8, 5, 9, 6, 14, 10, 11, 15], variables.comps
)
s = Solver()
s.add(ver, original_baby)
f = open('query.txt', 'w')
#st = s.sexpr()
f.write(str(s.assertions()))
f.close()
print(s.check())
