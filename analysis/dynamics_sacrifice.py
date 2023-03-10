'''
Dynamics of child- and adult sacrifice.
Not (currently) used in the paper.
VMP 2023-02-05: save as .svg and .pdf 
'''

import numpy as np 
import matplotlib.pyplot as plt 
from tqdm import tqdm 
import pandas as pd 
import networkx as nx 
from fun import transition_probabilities

# check the future warning 
configurations = np.loadtxt('../data/preprocessing/configurations.txt')
configuration_probabilities = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')

# setup 
labels = ['AS, CS', '~AS, ~CS', 'AS, ~CS', '~AS, CS']
label_type = [1, 2, 3, 4]
idx_first = 14 # adult sacrifice  
n_samples = 10000
df = transition_probabilities(configurations, 
                              configuration_probabilities,
                              idx_first,
                              n_samples)

# recode 
conversion_dict = {num:label for num, label in enumerate(labels)}
df['label_from'] = [conversion_dict.get(x) for x in df['type_from']] 
df['label_to'] = [conversion_dict.get(x) for x in df['type_to']]
df = df.sort_values(['type_from', 'type_to'],
                    ascending = [True, True])

# initialize network
G = nx.from_pandas_edgelist(df,
                            source = 'label_from',
                            target = 'label_to',
                            edge_attr = 'probability',
                            create_using = nx.DiGraph)

# edge labels
edge_width = []
edge_labels = {}
for x, y, attr in G.edges(data = True): 
    weight = attr['probability']
    edge_width.append(weight)
    edge_labels[(x, y)] = round(weight, 2)

# positions 
positions = [(1, 2), (1, 0), (0, 1), (2, 1)]
pos = {key:pos for key, pos in zip(labels, positions)}

# node labels 
node_labels = {}
for i in G.nodes(): 
    node_labels[i] = i

# edge labels (not well implemented in networkx)
## need the initial positions to make this work 
x = nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels);

## take those values out automatically ... ?
fig, ax = plt.subplots(dpi = 300, figsize = (8, 8))
plt.axis('off')
nx.draw_networkx_nodes(G, pos, node_size = 4500, linewidths = 2,
                       edgecolors = 'k',
                       node_color = 'white')
nx.draw_networkx_edges(G, pos, width = [x*5 for x in edge_width],
                       connectionstyle = "arc3,rad=0.2",
                       node_size = 5500)
nx.draw_networkx_labels(G, pos, node_labels)

# edge labels, laborious because networkx...
nudge_list = [(-0.15, 0.15), # (yes/yes, yes/no): 0.23 
              (-0.05, -0.05), # (yes/yes, no/yes): 0.22
              (0.05, -0.05), # (yes/no, yes/yes): 0.4
              (-0.05, -0.05), # (yes/no, no/no): 0.53
              (0.15, 0.15), # (no/yes, yes/yes): 0.4
              (-0.15, 0.15), # (no/yes, no/no): 0.53
              (0.15, 0.15), # (no/no, yes/no): 0.19
              (0.05, -0.05)] # (no/no, no/yes): 0.16
num = 0
for text, nudge in zip(x.values(), nudge_list): 
    probability = text.get_text()
    pos_x, pos_y = text.get_position()
    nudge_x, nudge_y = nudge 
    if num in [1, 3, 4, 6]: # not 0, 2, 5 (but this one needs to change)
        rotation = -50
    else: 
        rotation = 50 
    ax.text(x = pos_x + nudge_x,
            y = pos_y + nudge_y,
            s = probability,
            rotation = rotation,
            fontsize = 20,
            horizontalalignment = 'center',
            verticalalignment = 'center',
            color = 'black')
    num += 1
plt.savefig(f'../fig/pdf/sacrifice_transitions_{n_samples}.pdf')
plt.savefig(f'../fig/svg/sacrifice_transitions_{n_samples}.svg')

# specifically spartan 
## only the maximum likelihood configuration
spartans = pd.read_csv('..../data/preprocessing/entry_maxlikelihood.csv')
spartans = spartans[spartans['entry_name'].str.contains('Archaic Spartan')]
spartan_idx = spartans['config_id'].tolist()
spartan_conf = configurations[spartan_idx]
spartan_restricted = np.delete(spartan_conf, [idx_first, idx_first + 1], 1)

# configurations ignoring two indices (i.e. 2**18 rather than 2**20)
restricted_configurations = np.delete(configurations, [idx_first, idx_first + 1], 1)
restricted_configurations = np.unique(restricted_configurations, axis = 0)

spartan_idx_restricted = np.where(np.all(restricted_configurations == spartan_restricted, axis = 1))[0][0]

df = transition_probabilities(configurations, 
                              configuration_probabilities,
                              idx_first,
                              n_samples,
                              [spartan_idx_restricted])

# recode 
conversion_dict = {num:label for num, label in enumerate(labels)}
df['label_from'] = [conversion_dict.get(x) for x in df['type_from']] 
df['label_to'] = [conversion_dict.get(x) for x in df['type_to']]
df = df.sort_values(['type_from', 'type_to'],
                    ascending = [True, True])

# initialize network
G = nx.from_pandas_edgelist(df,
                            source = 'label_from',
                            target = 'label_to',
                            edge_attr = 'probability',
                            create_using = nx.DiGraph)

# edge labels
edge_width = []
edge_labels = {}
for x, y, attr in G.edges(data = True): 
    weight = attr['probability']
    edge_width.append(weight)
    edge_labels[(x, y)] = round(weight, 2)

# positions 
positions = [(1, 2), (1, 0), (0, 1), (2, 1)]
pos = {key:pos for key, pos in zip(labels, positions)}

# node labels 
node_labels = {}
for i in G.nodes(): 
    node_labels[i] = i

# edge labels (not well implemented in networkx)
## need the initial positions to make this work 
x = nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels);

## take those values out automatically ... ?
fig, ax = plt.subplots(dpi = 300, figsize = (8, 8))
plt.axis('off')
nx.draw_networkx_nodes(G, pos, node_size = 4500, linewidths = 2,
                       edgecolors = 'k',
                       node_color = 'white')
nx.draw_networkx_edges(G, pos, width = [x*5 for x in edge_width],
                       connectionstyle = "arc3,rad=0.2",
                       node_size = 5500)
nx.draw_networkx_labels(G, pos, node_labels)

# edge labels, laborious because networkx...
nudge_list = [(-0.15, 0.15), # (yes/yes, yes/no): 0.23 
              (-0.05, -0.05), # (yes/yes, no/yes): 0.22
              (0.05, -0.05), # (yes/no, yes/yes): 0.4
              (-0.05, -0.05), # (yes/no, no/no): 0.53
              (0.15, 0.15), # (no/yes, yes/yes): 0.4
              (-0.15, 0.15), # (no/yes, no/no): 0.53
              (0.15, 0.15), # (no/no, yes/no): 0.19
              (0.05, -0.05)] # (no/no, no/yes): 0.16
num = 0
for text, nudge in zip(x.values(), nudge_list): 
    probability = text.get_text()
    pos_x, pos_y = text.get_position()
    nudge_x, nudge_y = nudge 
    if num in [1, 3, 4, 6]: # not 0, 2, 5 (but this one needs to change)
        rotation = -50
    else: 
        rotation = 50 
    ax.text(x = pos_x + nudge_x,
            y = pos_y + nudge_y,
            s = probability,
            rotation = rotation,
            fontsize = 20,
            horizontalalignment = 'center',
            verticalalignment = 'center',
            color = 'black')
    num += 1
plt.savefig('../fig/pdf/sacrifice_spartan_maxlikelihood.pdf')
plt.savefig('../fig/svg/sacrifice_spartan_maxlikelihood.svg')
