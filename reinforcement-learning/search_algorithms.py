import numpy as np
import random
from copy import deepcopy

def writeVectorToFile(file_name, policy_vector):
	with open(file_name, 'w') as policy_file:
	    for policy in policy_vector:
	        policy_file.write("%d\n" % policy)

class SampleClass:
    def __init__(self, state, action, reward, next_state):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state

def analyze_file(filename):
    complete_sample_list = []
    with open(filename) as f:
        for i, line in enumerate(f):
	    	if i != 0:
	            temp = line.split(',')
	            s = int(temp[0])
	            a = int(temp[1])
	            r = int(temp[2])
	            s_new = int(temp[3])
	            new_samp = SampleClass(s, a, r, s_new)
	            complete_sample_list.append(new_samp)
    return complete_sample_list

def initQ():
    Q_dict = {} # (state, action) : q value
    for state in state_space:
        for action in action_space:
            Q_dict[state, action] = 0
    return Q_dict

def Sarsa(Q, complete_sample_list, alpha, gamma):
    for i in range(len(complete_sample_list)-1):
        sample = complete_sample_list[i]
        s_t = sample.state
        a_t = sample.action
        r_t = sample.reward
        
        next_sample = complete_sample_list[i+1]
        s_t_next = next_sample.state
        a_t_next = next_sample.action
        
        Q[s_t, a_t] += alpha * (r_t + gamma * Q[s_t_next, a_t_next] - Q[s_t, a_t])
    return Q


medium_complete_sample_list = analyze_file('large.csv')
state_space = [i for i in range(1, 10101010 + 1)]
action_space = [i for i in range(1, 125 + 1)]

Q = initQ()
newQ = Sarsa(Q, medium_complete_sample_list, 0.001, 0.95)

policy_vector = []
for i in range(len(state_space)):
    state = state_space[i]
    
    current_Q_list = []
    actions_taken = []
    for j in range(len(action_space)):
        action = action_space[j]
        current_Q_list.append(newQ[state, action])
        actions_taken.append(action)
        
    max_Q_val = max(current_Q_list)
    index = current_Q_list.index(max_Q_val)
    policy_vector.append(actions_taken[index])

writeVectorToFile('large6.policy', policy_vector)