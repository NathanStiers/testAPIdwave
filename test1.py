# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 13:24:06 2020

@author: nathan.stiers
"""

import networkx as nx

import matplotlib
matplotlib.use("agg")   # select backend
import matplotlib.pyplot as plt


def visualize_map(nodes, edges, sample, node_positions=None):
    # Set up graph
    G = nx.Graph(edges)

    lone_nodes = set(nodes) - set(G.nodes)  # nodes without edges
    for lone_node in lone_nodes:
        G.add_node(lone_node)

    # Grab the colors selected by sample
    color_labels = [k for k, v in sample.items() if v == 1]

    # Get color order to match that of the graph nodes
    for label in color_labels:
        name, color = label.split("_")
        G.nodes[name]["color"] = color
    color_map = [color for name, color in G.nodes(data="color")]

    # Draw graph
    nx.draw_networkx(G, pos=node_positions, with_labels=True,
                     node_color=color_map, font_color="w", node_size=400)

    # Save graph
    filename = "graph.png"
    plt.savefig(filename)
    print("The graph is saved in '{}'.".format(filename))
    
import dwavebinarycsp
from hybrid.reference.kerberos import KerberosSampler

#from utilities import visualize_map


class Province:
    def __init__(self, name):
        self.name = name
        self.red = name + "_r"
        self.green = name + "_g"
        self.blue = name + "_b"
        self.yellow = name + "_y"


# Set up provinces
bc = Province("bc")   # British Columbia
ab = Province("ab")   # Alberta
sk = Province("sk")   # Saskatchewan
mb = Province("mb")   # Manitoba
on = Province("on")   # Ontario
qc = Province("qc")   # Quebec
nl = Province("nl")   # Newfoundland and Labrador
nb = Province("nb")   # New Brunswick
pe = Province("pe")   # Prince Edward Island
ns = Province("ns")   # Nova Scotia
yt = Province("yt")   # Yukon
nt = Province("nt")   # Northwest Territories
nu = Province("nu")   # Nunavut

provinces = [bc, ab, sk, mb, on, qc, nl, nb, pe, ns, yt, nt, nu]

# Set up province neighbours (i.e. shares a border)
neighbours = [(bc, ab),
              (bc, nt),
              (bc, yt),
              (ab, sk),
              (ab, nt),
              (sk, mb),
              (sk, nt),
              (mb, on),
              (mb, nu),
              (on, qc),
              (qc, nb),
              (qc, nl),
              (nb, ns),
              (yt, nt),
              (nt, nu)]

# Initialize constraint satisfaction problem
csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)
not_both = {(0, 1), (1, 0), (0, 0)}
select_one = {(0, 0, 0, 1),
              (0, 0, 1, 0),
              (0, 1, 0, 0),
              (1, 0, 0, 0)}

# Apply one color constraint
for p in provinces:
    csp.add_constraint(select_one, {p.red, p.green, p.blue, p.yellow})

# Apply no color sharing between neighbours
for x, y in neighbours:
    csp.add_constraint(not_both, {x.red, y.red})
    csp.add_constraint(not_both, {x.green, y.green})
    csp.add_constraint(not_both, {x.blue, y.blue})
    csp.add_constraint(not_both, {x.yellow, y.yellow})

# Combine constraints to form a BQM
bqm = dwavebinarycsp.stitch(csp)

# Solve BQM
solution = KerberosSampler().sample(bqm)
best_solution = solution.first.sample
print("Solution: ", best_solution)

# Verify
is_correct = csp.check(best_solution)
print("Does solution satisfy our constraints? {}".format(is_correct))


# Visualize the solution
# Note: The following is purely for visualizing the output and is not necessary
# for the demo.

# Hard code node positions to be reminiscent of the map of Canada
node_positions = {"bc": (0, 1),
                  "ab": (2, 1),
                  "sk": (4, 1),
                  "mb": (6, 1),
                  "on": (8, 1),
                  "qc": (10, 1),
                  "nb": (10, 0),
                  "ns": (12, 0),
                  "pe": (12, 1),
                  "nl": (12, 2),
                  "yt": (0, 3),
                  "nt": (2, 3),
                  "nu": (6, 3)}

nodes = [u.name for u in provinces]
edges = [(u.name, v.name) for u, v in neighbours]
visualize_map(nodes, edges, best_solution, node_positions=node_positions)