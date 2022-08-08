import random
import networkx as nx
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import glob

# Parse arguments
parser = argparse.ArgumentParser(description="Parse the arguments")
parser.add_argument('--node', default=15, type=int, help="The number of nodes")
parser.add_argument('--probability', default=0.5, type=float, help="Connection possibility")
parser.add_argument('--num_activated', default=1, type=int, help="Activated nodes")
parser.add_argument('--save', default='False', type=str, choices=['True', 'False'], help="Save the generated GIF")
parser.add_argument('--speed', default=200, type=int, help="Interval")
args = parser.parse_args()

node = args.node
p = args.probability
if p > 1 or p < 0:
    raise "Invalid probability! "
num_activated = args.num_activated

# Initialize a graph
nodes = list(range(node))
graph = nx.Graph()
graph.add_nodes_from(nodes)

# Randomly set thresholds, keep them in a dictionary
thresholds = np.random.rand(node)
weighted = {}
for i in range(len(nodes)):
    weighted[str(nodes[i])] = round(thresholds[i], 3)

labels = {
    int(n): n + '\nweight=' + str(weighted[n])
    for n in weighted
}

edges = {}
# Initialize
for n in nodes:
    edges[str(n)] = []

# Randomly connect nodes with possibility p
for i in range(len(nodes)):
    for j in range(i+1, len(nodes)):
        # If choice is 1 then add an edge
        choice = np.random.choice([0, 1], p=[1-p, p])
        if choice == 1:
            edges[str(i)].append(j)
            edges[str(j)].append(i)
            graph.add_edge(i, j)

# Randomly activate nodes
activated = random.sample(nodes, num_activated)
non_activated = [n for n in nodes if n not in activated]

# Start infection, stop when no more changeable nodes
sequence = [activated.copy()]
activation = [0]
while len(activation) != 0:
    # loop over all the non-activated nodes
    activation = []
    for n in non_activated:
        # Pick all the neighbors
        neighbors = edges[str(n)]
        activated_neighbors = [ne for ne in neighbors if ne in activated]
        # Work out the influence
        influence = 0
        for ne in activated_neighbors:
            influence += weighted[str(ne)]

        # Compare the influence and the threshold
        if weighted[str(n)] < influence:
            activation.append(n)
            activated.append(n)
            non_activated.remove(n)
    sequence.append(activation)

# Build a figure
fig, ax = plt.subplots(figsize=(15, 10))

# Initialize colors
color = (np.random.random(), np.random.random(), np.random.random())
color_map = [color]*node

def update(t):
    ax.clear()
    ax.set_title("Linear Threshold\n nodes=%d, p_connection=%.3f" % (node, p))
    # Set colors
    color = (np.random.random(), np.random.random(), np.random.random())
    for n in nodes:
        if n in sequence[t]:
            color_map[n] = color
    nx.draw(graph, pos=nx.circular_layout(graph), ax=ax, edge_color="gray", node_color=color_map, node_size=750, alpha=0.7)
    nx.draw_networkx_labels(graph, pos=nx.circular_layout(graph), labels=labels, font_size=10, font_color='red')


ani = FuncAnimation(fig, update, frames=len(sequence), interval=args.speed, repeat=False)
if args.save == "True":
    num = len(glob.glob(r'linear_threshold*.gif'))
    ani.save("linear_threshold%d.gif" % (num), writer='pillow')

else:
    plt.show()
