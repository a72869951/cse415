'''YourUWNetID_VI.py
(rename this file using your own UWNetID.)

Value Iteration for Markov Decision Processes.
'''

# Edit the returned name to ensure you get credit for the assignment.
def student_name():
    return "Your Zeng, Junhao" # For an autograder.

Vkplus1 = {}
Q_Values_Dict = {}

def one_step_of_VI(S, A, T, R, gamma, Vk):
    '''S is list of all the states defined for this MDP.
    A is a list of all the possible actions.
    T is a function representing the MDP's transition model.
    R is a function representing the MDP's reward function.
    gamma is the discount factor.
    The current value of each state s is accessible as Vk[s].
    '''
    global Q_Values_Dict
    # update each state for one iteration, and initialize delta_max = 0
    delta_max = 0
    for s in S:

        # update each action for each state, and initialize Vkplus = 0
        Vkplus1[s] = 0
        for a in A:
            Q_Values_Dict[(s, a)] = sum([T(s, a, sp) * (R(s, a, sp) + gamma * Vk[sp]) for sp in S])

            # update Vk1 with largest Q_Values_Dict[(s, a)]
            if Q_Values_Dict[(s, a)] > Vkplus1[s]:
                Vkplus1[s] = Q_Values_Dict[(s, a)]
        delta_max = max(abs(Vkplus1[s] - Vk[s]), delta_max)
    '''Your code should fill the dictionaries Vkplus1 and Q_Values_dict
    with a new value for each state, and each q-state, and assign them
    to the state's and q-state's entries in the dictionaries, as in
       Vkplus1[s] = new_value
       Q_Values_Dict[(s, a)] = new_q_value
    
    Also determine delta_max, which we define to be the maximum
    amount that the absolute value of any state's value is changed
    during this iteration.
    '''
    return (Vkplus1, delta_max)


def return_Q_values(S, A):
    '''Return the dictionary whose keys are (state, action) tuples,
    and whose values are floats representing the Q values from the
    most recent call to one_step_of_VI. This is the normal case, and
    the values of S and A passed in here can be ignored.
    However, if no such call has been made yet, use S and A to
    create the answer dictionary, and use 0.0 for all the values.
    '''

    # when no such call has been made yet, create the answer dictionary, and use 0.0
    # for all the values
    global Q_Values_Dict
    if len(Q_Values_Dict) == 0:
        for s in S:
            for a in A:
                Q_Values_Dict[(s, a)] = 0
    return Q_Values_Dict # placeholder

Policy = {}
def extract_policy(S, A):
    '''Return a dictionary mapping states to actions. Obtain the policy
    using the q-values most recently computed.  If none have yet been
    computed, call return_Q_values to initialize q-values, and then
    extract a policy.  Ties between actions having the same (s, a) value
    can be broken arbitrarily.
    '''
    global Policy
    Policy = {}

    # Add code here
    # if none have yet been computed, call return_Q_values to initialize q-values
    # then extract a policy
    if len(Policy) == 0:
        Q_Values_Dict = return_Q_values(S,A)
    for s in S:
        temp = 0
        for a in A:
            if Q_Values_Dict[s, a] > temp:
                temp = Q_Values_Dict[s, a]
                Policy[s] = a
    return Policy

def apply_policy(s):
    '''Return the action that your current best policy implies for state s.'''

    global Policy
    return Policy[s] # placeholder


