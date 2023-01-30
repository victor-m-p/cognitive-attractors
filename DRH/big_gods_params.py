'''
VMP 2023-01-02: 
Visualize the paratmers (Jij, hi) versus surface-level correlations. 
Produces figure 3A, 3B. 
'''

import itertools 
import pandas as pd 
import matplotlib.pyplot as plt 
import networkx as nx 
import numpy as np
from fun import *

# helper functions
def node_edge_lst(n, corr_J, means_h): 
    nodes = [node+1 for node in range(n)]
    comb = list(itertools.combinations(nodes, 2))
    d_edgelst = pd.DataFrame(comb, columns = ['n1', 'n2'])
    d_edgelst['weight'] = corr_J
    d_nodes = pd.DataFrame(nodes, columns = ['n'])
    d_nodes['size'] = means_h
    d_nodes = d_nodes.set_index('n')
    dct_nodes = d_nodes.to_dict('index')
    return d_edgelst, dct_nodes

def create_graph(d_edgelst, dct_nodes,): 

    G = nx.from_pandas_edgelist(
        d_edgelst,
        'n1',
        'n2', 
        edge_attr=['weight', 'weight_abs'])

    # assign size information
    for key, val in dct_nodes.items():
        G.nodes[key]['size'] = val['size']

    # label dict
    labeldict = {}
    for i in G.nodes(): 
        labeldict[i] = i
    
    return G, labeldict

# PLOT PARAMETERS 
n_nodes, n_nan, n_rows, n_entries = 20, 5, 455, 407
A = np.loadtxt(f'../data/mdl_experiments/matrix_questions_{n_nodes}_maxna_{n_nan}_nrows_{n_rows}_entries_{n_entries}.txt.mpf_params.dat')
n_J = int(n_nodes*(n_nodes-1)/2)
J = A[:n_J] 
h = A[n_J:]

# make it 1-20, and cross-reference that with the related question IDs. 
d_edgelst, dct_nodes = node_edge_lst(n_nodes, J, h)
d_edgelst = d_edgelst.assign(weight_abs = lambda x: np.abs(x['weight']))

# try with thresholding 
d_edgelst_sub = d_edgelst[d_edgelst['weight_abs'] > 0.15]
G, labeldict = create_graph(d_edgelst_sub, dct_nodes)

# setup 
seed = 1
cmap = plt.cm.coolwarm
cutoff_n = 15

# position
pos = nx.nx_agraph.graphviz_layout(G, prog = "fdp")

# a few manual tweaks 
x, y = pos[10]
pos[10] = (x, y+30)
x, y = pos[5]
pos[5] = (x, y+50)
x, y = pos[1]
pos[1] = (x+15, y)

# make a new network
focus_list = [11, 12, 13]
d_edgelst = d_edgelst[(d_edgelst['n1'].isin(focus_list)) | (d_edgelst['n2'].isin(focus_list))]

G, labeldict = create_graph(d_edgelst, dct_nodes)

# plot 
fig, ax = plt.subplots(figsize = (6, 4), facecolor = 'w', dpi = 500)
plt.axis('off')

size_lst = list(nx.get_node_attributes(G, 'size').values())
weight_lst = list(nx.get_edge_attributes(G, 'weight').values())
threshold = sorted([np.abs(x)/5 for x in weight_lst], reverse=True)[cutoff_n]
weight_lst_filtered = [x if np.abs(x)>threshold else 0 for x in weight_lst]

# vmin, vmax edges
vmax_e = np.max(list(np.abs(weight_lst)))
vmin_e = -vmax_e

# vmin, vmax nodes
vmax_n = np.max(list(np.abs(size_lst)))
vmin_n = -vmax_n

size_abs = [abs(x)*3000 for x in size_lst]
weight_abs = [abs(x)*15 for x in weight_lst_filtered]

nx.draw_networkx_nodes(
    G, pos, 
    node_size = 600,
    node_color = size_lst, 
    edgecolors = 'black',
    linewidths = 0.5,
    cmap = cmap, vmin = vmin_n, vmax = vmax_n 
)
nx.draw_networkx_edges(
    G, pos,
    width = weight_abs, 
    edge_color = weight_lst, 
    alpha = 0.7, 
    edge_cmap = cmap, edge_vmin = vmin_e, edge_vmax = vmax_e)
nx.draw_networkx_labels(G, pos, font_size = 14, labels = labeldict)
# add to axis
sm_edge = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin = vmin_e, vmax=vmax_e))
sm_edge._A = []
sm_node = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin = vmin_n, vmax=vmax_n))
sm_node._A = []
axis = plt.gca()
plt.subplots_adjust(bottom=0.1, right=1, left=0, top=1)
ax_edge = plt.axes([0.05, 0, 0.90, 0.05])
ax_node = plt.axes([0.05, -0.2, 0.9, 0.05])
plt.colorbar(sm_edge, cax = ax_edge, orientation='horizontal')
plt.colorbar(sm_node, cax = ax_node, orientation='horizontal')
ax.text(0.24, -0.03, r'Pairwise couplings (J$_{ij}$)', size=20, transform=ax.transAxes)
ax.text(0.3, -0.25, r'Local fields (h$_i$)', size = 20, transform = ax.transAxes)
plt.savefig('../fig/parameters.pdf', bbox_inches='tight')

