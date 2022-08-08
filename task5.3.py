import random
import networkx as nx
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import glob

# Parse arguments
parser = argparse.ArgumentParser(description="Parse the arguments")
parser.add_argument('--node', default=20, type=int, help="The number of nodes")
parser.add_argument('--p_connection', default=0.2, type=float, help="Connection probability")
parser.add_argument('--p_infection', default=0.5, type=float, help="Infection probability")
parser.add_argument('--p_cure', default=0.5, type=float, help="Cured probability")
parser.add_argument('--iterations', default=15, type=int, help="Iterating times")
parser.add_argument('--save', default='False', type=str, choices=['True', 'False'], help="Save the generated GIF")
parser.add_argument('--speed', default=200, type=int, help="Interval")
args = parser.parse_args()

node = args.node
p_connection = args.p_connection
p_infection = args.p_infection
p_cure = args.p_cure
iterations = args.iterations

# Check validity
if p_connection < 0 or p_connection > 1:
    raise "Invalid probability! "
if p_infection < 0 or p_infection > 1:
    raise "Invalid probability! "
if p_cure < 0 or p_cure > 1:
    raise "Invalid probability! "
if iterations < 1:
    raise "Invalid iterations! "

# Initialize a graph
nodes = list(range(node))
graph = nx.Graph()
graph.add_nodes_from(nodes)

# Set the labels for each node
labels = {}
for n in graph.nodes():
    labels[node] = str(n)

edges = {}
# Initialize
for n in nodes:
    edges[str(n)] = []

# Randomly connect nodes with possibility p
for i in range(len(nodes)):
    for j in range(i+1, len(nodes)):
        # If choice is 1 then add an edge
        choice = np.random.choice([0, 1], p=[1-p_connection, p_connection])
        if choice == 1:
            edges[str(i)].append(j)
            edges[str(j)].append(i)
            graph.add_edge(i, j)

# Set infective nodes
infected = []
for n in nodes:
    choice = np.random.choice([0, 1], p=[1 - p_infection, p_infection])
    if choice == 1:
        infected.append(n)
not_infected = [n for n in nodes if n not in infected]
inf_sequence = [[], infected.copy()]

for i in range(iterations-1):
    new_infected = []
    new_cured = []
    # Check the connected nodes
    for inf in infected:
        neighbors = [n for n in edges[str(inf)] if n in not_infected]
        # Infect the neighbors
        for n in neighbors:
            if n in new_infected:
                continue
            else:
                choice = np.random.choice([0, 1], p=[1 - p_infection, p_infection])
                if choice == 1:
                    new_infected.append(n)
        # Cure itself
        choice = np.random.choice([0, 1], p=[1 - p_cure, p_cure])
        if choice == 1:
            new_cured.append(inf)

    # Update the status
    for n in new_cured:
        infected.remove(n)
        not_infected.append(n)

    for n in new_infected:
        infected.append(n)
        not_infected.remove(n)

    # Append to the sequence
    inf_sequence.append(infected.copy())

# Build a figure
fig, ax = plt.subplots(figsize=(10, 7))

# Initialize colors, blue means not infected while red means infected
color1, color2 = 'blue', 'red'
color_map = [color1]*node
for inf in inf_sequence[0]:
    color_map[inf] = color2


def update(t):
    ax.clear()
    ax.set_title("Blue node: Normal node, Red node: Infected node\n Cure/Infect in %d iterations" % iterations)

    # Set colors
    for n in nodes:
        if n in inf_sequence[t]:
            color_map[n] = color2
        else:
            color_map[n] = color1
    nx.draw(graph, pos=nx.circular_layout(graph), ax=ax, edge_color="gray", node_color=color_map, label=labels,
            with_labels=True, alpha=0.5)


ani = FuncAnimation(fig, update, frames=iterations+1, interval=args.speed, repeat=False)
if args.save == "True":
    num = len(glob.glob(r'pandemic*.gif'))
    ani.save("pandemic%d.gif" % (num), writer='pillow')

else:
    plt.show()
