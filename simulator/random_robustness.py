'''
    Simulations to know the number of nodes needed by an attacker to take control of one random address.
    Control is taken when the attacker control R nodes around the random address.
'''

import random
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

# Run one simulation of taking control of nodes until full control of at least one address.
# Control is obtained when a sufficient number (redundancy_val) of consecutive nodes are controlled.
# note: node space is like a circle, end and beginning are linked.
def random_control(nb_nodes, redundancy_val, max_nodes=None):
    table = [0]*nb_nodes
    controled_nodes = 0
    while(True):
        # choose a random node not already controlled
        # note: this is slow when already a lot of nodes are controlled
        # faster algorithm ?
        r = None
        while r == None or table[r]==1: 
            r = random.randint(0,nb_nodes-1)
        
        # Take control of this node
        table[r] = 1
        controled_nodes += 1
        
        # Check the number of consecutive controlled nodes from index r
        # Check in both directions (right and left)
        # Modulo used because the id space is like a circle.
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

# Average number of nodes needed to take control
# using nb_simul simulations.
def simulate_control(nb_nodes, redundancy_val, nb_simul):
    total = 0
    for i in range(nb_simul):
        total += random_control(nb_nodes, redundancy_val)
    return int(round(total/nb_simul))

# Graph showing the average number of nodes needed to take control in function of the redundancy factor
# for a given fixed number of nodes in the network.
def plot_graph_fixednbnodes(nb_nodes, redundancy_max, nb_simul, filename=None):
    x = [0]*redundancy_max
    result = [0]*redundancy_max
    for redundancy_val in range(1, redundancy_max+1):
        x[redundancy_val-1] = redundancy_val
        result[redundancy_val-1] = simulate_control(nb_nodes, redundancy_val, nb_simul)
    plt.figure()
    plt.plot(x, result)
    if filename:
        plt.savefig(filename)
    else:
        plt.show()


# Probability of controlling one address when we control a given percentage of the network.
def control_prob(nb_nodes, redundancy_val, percent_controled, nb_simul):
    nb_controled_nodes = int(round((nb_nodes * percent_controled)))
    success_nb = 0
    for i in range(nb_simul):
        if nb_controled_nodes >= random_control(nb_nodes, redundancy_val, max_nodes = nb_controled_nodes):
            success_nb += 1
    return success_nb / nb_simul

# Graph of the probability of controlling one address in function of the redundancy factor
# for a fixed given percentage of the network controlled by the attacker,
# in a network with a fixed number of nodes.
def plot_control_prob(nb_nodes, redundancy_max, percent_controled_list, nb_simul, filename = None):
    print("Parameters:")
    print("Nodes: ", nb_nodes)
    print("Redundancy max: ", redundancy_max) 
    print("Control percent: ", percent_controled_list) 
    print("Nb simulations: ", nb_simul)

    plt.figure()
    ax = plt.figure().gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    
    for percent_controled in percent_controled_list:
        x = [0]*redundancy_max
        result = [0]*redundancy_max
        for redundancy_val in range(1, redundancy_max+1):
            x[redundancy_val-1] = redundancy_val
            result[redundancy_val-1] = control_prob(nb_nodes, redundancy_val, percent_controled, nb_simul)
            print("Percent controlled:", percent_controled, ", Redundancy:", redundancy_val, "... Finished")
        plt.semilogy(x, result, label=str(int(percent_controled*100)) + "% control")
    
    plt.legend(loc='upper right')
    plt.xlabel("R, redundancy factor")    
    plt.ylabel("successful attack probability")
    plt.title("Probability of successful attack in network of " + str(nb_nodes) + " nodes")
    
    if filename:
        plt.savefig(filename)
    else:
        plt.show()


# Proportion of the network that we need to control in order to take control of one address
# with a probability above some threshold.
def needed_control(nb_nodes, redundancy_val, threshold_prob, nb_simul):
    result_list = np.zeros(nb_simul)
    for i in range(nb_simul):
        result_list[i] = random_control(nb_nodes, redundancy_val)
    percentile_value = np.percentile(result_list, threshold_prob*100)
    return percentile_value / nb_nodes

# Graph of the proportion of network needed by the attacker
# to take control with some given probability threshold,
# in function of the redundancy factor, for a network with a fixed number of nodes.
def plot_needed_control(nb_nodes_list, redundancy_max, threshold_prob, nb_simul, filename = None):
    print("Parameters:")
    print("Nodes: ", nb_nodes_list)
    print("Redundancy max: ", redundancy_max) 
    print("Attack success threshold: ", threshold_prob) 
    print("Nb simulations: ", nb_simul)
    
    plt.figure()
    ax = plt.figure().gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    
    for nb_nodes in nb_nodes_list:
        x = [0]*redundancy_max
        result = [0]*redundancy_max
        for redundancy_val in range(1, redundancy_max+1):
            x[redundancy_val-1] = redundancy_val
            result[redundancy_val-1] = needed_control(nb_nodes, redundancy_val, threshold_prob, nb_simul)
            print("Nodes:", nb_nodes, ", Redundancy:", redundancy_val, "... Finished")
        plt.plot(x, result, label=str(nb_nodes) + " nodes")
    
    plt.legend(loc='upper left')
    plt.xlabel("R, redundancy factor")    
    plt.ylabel("needed network proportion")
    plt.title("Proportion of network needed for " + str(threshold_prob*100) + "% attack success")
    
    if filename:
        plt.savefig(filename)
    else:
        plt.show()


if __name__ == '__main__':
    plot_needed_control([100, 1000, 10000], 40, 0.01, 600, "needed_control1.png")
    
    plot_control_prob(1000, 10, [0.1], 100000, "control_prob1.png")
    
    plot_control_prob(1000, 22, [0.1, 0.2, 0.3, 0.4, 0.5], 10000, "control_prob2.png")
