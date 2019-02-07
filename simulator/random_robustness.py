#Simulations to know the number of nodes needed by an attacker to take control of one random address
#control is taken when the attacker control R nodes around the random address

import random
import matplotlib.pyplot as plt
import numpy as np

#run one simulation of taking control of nodes until full control of at least one address
#full control is obtained when a sufficient number of nodes (redundancy_val) are controlled consecutively
#note: node space is like a circle, end and beginning are linked (this is why we use modulo nb_nodes) 
def random_control(nb_nodes, redundancy_val, max_nodes=None):
    table = [0]*nb_nodes
    controled_nodes = 0
    while(True):
        #choose a random node not already controlled
        #note: this is slow when already a lot of nodes are controlled
        #faster algorithm ?
        r = None
        while r == None or table[r]==1: 
            r = random.randint(0,nb_nodes-1)
        
        #take control
        table[r] = 1
        controled_nodes += 1
        
        #check the number of consecutive controlled nodes from index r
        #check in both directions (right and left)
        length = 0
        for i in range(0, nb_nodes):
            idx = (r + i) % nb_nodes
            if table[idx]==1:
                length += 1
            else:
                break
        for i in range(0, nb_nodes):
            idx = (r - 1 - i) % nb_nodes
            if table[idx]==1:
                length += 1
            else:
                break
        if length >= redundancy_val:
            return controled_nodes
        
        if max_nodes != None and controled_nodes > max_nodes:
            return controled_nodes

#Average number of nodes needed to take control
#using nb_simul simulations
def simulate_control(nb_nodes, redundancy_val, nb_simul):
    total = 0
    for i in range(nb_simul):
        total += random_control(nb_nodes, redundancy_val)
    return int(round(total/nb_simul))

#graph showing the average number of nodes needed to take control in function of the redundancy factor
#for a given fixed number of nodes in the network
def plot_graph_fixednbnodes(nb_nodes, redundancy_max, nb_simul):
    x = [0]*redundancy_max
    result = [0]*redundancy_max
    for redundancy_val in range(1, redundancy_max+1):
        x[redundancy_val-1] = redundancy_val
        result[redundancy_val-1] = simulate_control(nb_nodes, redundancy_val, nb_simul)
    plt.figure()
    plt.plot(x, result)
    plt.show()

#Probability of controlling one address when we control a given percentage of the network
def control_prob(nb_nodes, redundancy_val, percent_controled, nb_simul):
    nb_controled_nodes = int(round((nb_nodes * percent_controled)))
    success_nb = 0
    for i in range(nb_simul):
        if nb_controled_nodes >= random_control(nb_nodes, redundancy_val, max_nodes = nb_controled_nodes):
            success_nb += 1
    return success_nb / nb_simul

#graph of the probability of controlling one address in function of the redundancy factor
#for a fixed given percentage of the network controlled by the attacker, in a network with a fixed number of nodes
def plot_control_prob(nb_nodes, redundancy_max, percent_controled, nb_simul):
    x = [0]*redundancy_max
    result = [0]*redundancy_max
    for redundancy_val in range(1, redundancy_max+1):
        x[redundancy_val-1] = redundancy_val
        result[redundancy_val-1] = control_prob(nb_nodes, redundancy_val, percent_controled, nb_simul)
    plt.figure()
    plt.semilogy(x, result)
    plt.show()   

#Proportion of the network that we need to control in order to take control of one address
#with a probability above some threshold
def needed_control(nb_nodes, redundancy_val, threshold_prob, nb_simul):
    result_list = np.zeros(nb_simul)
    for i in range(nb_simul):
        result_list[i] = random_control(nb_nodes, redundancy_val)
    percentile_value = np.percentile(result_list, threshold_prob*100)
    return percentile_value / nb_nodes

#graph of the proportion of network needed by the attacker
#to take control with some given probability threshold
#in function of the redundancy factor, for a network with a fixed number of nodes
def plot_needed_control(nb_nodes, redundancy_max, threshold_prob, nb_simul):
    x = [0]*redundancy_max
    result = [0]*redundancy_max
    for redundancy_val in range(1, redundancy_max+1):
        x[redundancy_val-1] = redundancy_val
        result[redundancy_val-1] = needed_control(nb_nodes, redundancy_val, threshold_prob, nb_simul)
    plt.figure()
    plt.plot(x, result)
    plt.show()       

#draw some interesting plots
#TODO : axis legend, graph title...

#number of average nodes needed by attacker to have a successful attack in function of the redundancy factor
#in a network of 100, 1.000, 10.000, 100.000 nodes
plot_graph_fixednbnodes(100, 50, 500)
plot_graph_fixednbnodes(1000, 50, 500)
plot_graph_fixednbnodes(10000, 50, 30)
plot_graph_fixednbnodes(100000, 30, 10)

#probability of taking control when the attacker controls half of the nodes
#in a network of 100, 1000, 10000 nodes
#last number is the number of simulations for each redundancy factor
#last number = number of simulations for each point
plot_control_prob(100, 20, 0.5, 100000)
plot_control_prob(1000, 20, 0.5, 100000)
plot_control_prob(10000, 20, 0.1, 10000)

#probability of taking control when the attacker controls 1000 nodes in a network of 1M nodes
#last number = 1000 simulations per point (meaning we cannot show probabilities lower than 10^-3) 
plot_control_prob(1000000, 20, 0.001, 1000)

#same plot using 10000 simulations (meaning we cannot show probabilities lower than 10^-4) 
plot_control_prob(1000000, 20, 0.001, 10000)

#proportion of the network needed by an attacker to control at least one address with 1% probability
#in a network of 100 nodes
plot_needed_control(100, 50, 0.01, 1000)

#same with 90% probability
plot_needed_control(100, 30, 0.9, 1000)

#90% success of attack in network of 1000 nodes
plot_needed_control(1000, 30, 0.9, 1000)

#90% success of attack in network of 10000 nodes
plot_needed_control(10000, 30, 0.9, 200)

#1% success in network of 10000 nodes
plot_needed_control(10000, 30, 0.01, 200)

#1% success in network of 100.000 nodes
plot_needed_control(100000, 30, 0.01, 1000)
