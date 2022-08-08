import networkx as nx
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import glob

# Parse arguments
parser = argparse.ArgumentParser(description="Parse the arguments")
parser.add_argument('--mode', default='WS', choices=['WS', 'NW'], help="Graph type")
parser.add_argument('--node', default=10, type=int, help="The number of nodes")
parser.add_argument('--k', default=2, type=int)
parser.add_argument('--probability', default=0.5, type=float, help="Connection probability")
parser.add_argument('--save', default='False', type=str, choices=['True', 'False'], help="Save the generated GIF")
parser.add_argument('--speed', default=200, type=int, help="Interval")
args = parser.parse_args()

mode = args.mode
node = args.node
k = args.k

# Check validity
if 2*k > node-1:
    raise "Cannot generate graph!"

# Initialize a graph
nodes = list(range(node))

# Set the labels for each node
labels = {}
for n in nodes:
    labels[n] = str(n)

# This is used for edge storage
edges = []
for i in range(len(nodes)):
    for add in range(k):
        # Make sure that (u, v) satisfies u<v
        if (i+add+1) % node > i:
            edges.append([i, (i+add+1) % node])
        else:
            edges.append([(i + add + 1) % node, i])


# Store the changes
edges_rand = [edges]
if mode == 'WS':
    # Random reconnections
    for i in range(len(nodes)):
        # Find all the edges
        connected = [e for e in edges if e[0] == i]

        for j in range(len(connected)):
            new = edges_rand[-1].copy()
            # Find the index
            index = [ind for ind in range(len(new)) if (connected[j][0] == new[ind][0] and connected[j][1] == new[ind][1])][0]

            # Choose another node randomly
            new_node = np.random.choice([n for n in range(node) if n != i])
            if new_node < i:
                new_connection = [new_node, i]
            else:
                new_connection = [i, new_node]

            # If there are more than one connections
            while new_connection in new:
                if new_connection == new[index]:
                    break
                else:
                    new_node = np.random.choice([n for n in range(node) if n != i])
                    if new_node < i:
                        new_connection = [new_node, i]
                    else:
                        new_connection = [i, new_node]

            # Change the element
            new[index] = new_connection
            edges_rand.append(new)


else:
    probability = args.probability
    if probability > 1 or probability < 0:
        raise "Invalid possibility! "

    # Random connections
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            new = edges_rand[-1].copy()
            # No loop
            if i == j: continue

            choice = np.random.choice([0, 1], p=[1 - probability, probability])
            if choice == 1:
                if i < j:
                    if [i, j] not in new:
                        new.append([i, j])

                else:
                    if [j, i] not in new:
                        new.append([j, i])
                edges_rand.append(new)



# Build a figure
fig, ax = plt.subplots(figsize=(6, 4))


def update(t):
    ax.clear()
    # Generate a new graph
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges_rand[t])
    nx.draw(graph, pos=nx.circular_layout(graph), ax=ax, edge_color="gray")
    nx.draw_networkx_labels(graph, pos=nx.circular_layout(graph), labels=labels, font_size=10, font_color='w')
    if t == len(edges_rand)-1:
        shortest_path = nx.average_shortest_path_length(graph)
        avg_clustering = nx.average_clustering(graph)
        ax.set_title("Mode: %s, nodes=%d\n"
        "shortest path=%.3f, average clustering=%.3f" % (mode, node, shortest_path, avg_clustering))
    else:
        ax.set_title("Mode: %s, nodes=%d\n"
                    % (mode, node))


ani = FuncAnimation(fig, update, frames=len(edges_rand), interval=args.speed, repeat=False)
if args.save == "True":
    num = len(glob.glob(r'%s*.gif' % mode))
    ani.save("%s network %d.gif" % (mode, num), writer='pillow')

else:
    plt.show()