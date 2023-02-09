'''
VMP 2023-02-05: experimental approaches to attractors
Not used in the paper (currently). 
'''

import pandas as pd 
import numpy as np 
import os 
import re

path = '../data/analysis/max_attractor'
files = os.listdir(path)

## only consider the end attractor
termination_list = []
for file in files: 
    config_orig = int(re.match(r'idx(\d+).csv', file)[1])
    d = pd.read_csv(f'{path}/{file}')
    data_num_timesteps = len(d)
    if data_num_timesteps == 0: 
        termination_list.append((config_orig, config_orig))
    else: 
        config_terminate = d[d['timestep'] == data_num_timesteps - 1]['config_to'].tolist()[0]
        termination_list.append((config_orig, config_terminate)) 

termination_df = pd.DataFrame(termination_list,
                              columns = ['initial', 'attractor'])        

termination_sum = termination_df.groupby('attractor').size().reset_index(name = 'count')
termination_sum = termination_sum.sort_values('count', ascending = False)

# get all maximum likelihood configurations in here
entry_maxlikelihood = pd.read_csv('..../data/preprocessing/entry_maxlikelihood.csv')
termination_sum = termination_sum.rename(columns = {'attractor': 'config_id'})

# merge
termination_entries = entry_maxlikelihood.merge(termination_sum, on = 'config_id', how = 'inner')

# for each of these, pick a label: 
pd.set_option('display.max_colwidth', None)
termination_list = termination_entries.groupby('config_id')['entry_name'].apply(lambda x: " & ".join(x)).reset_index(name = 'entries')
termination_probs = termination_entries[['config_id', 'config_prob', 'count']].drop_duplicates()
termination_final = termination_list.merge(termination_probs, on = 'config_id', how = 'inner')
termination_final = termination_final[['config_id', 'config_prob', 'count', 'entries']]
termination_final = termination_final.sort_values('count', ascending = False)

# to latex 
termination_latex = termination_final.to_latex(index=False)
with open('../tables/termination_states_260.txt', 'w') as f: 
    f.write(termination_latex)

## slightly weird because this ignores all 
## intermediate "sub-attractors", and for instance
## means that the ancient egyptians should be empty
## because it is a neighbor to the cistercians. 

### new and crazy idea ### 
# so ... not considering the initial step ...
# only considering from the second step of all of the dataframes 
# but... what if the second step terminates ... 
# there should still be some that get there
# but we should go back and review this possibility

files = os.listdir(path)

## only consider the end attractor
termination_list = []
for file in files: 
    config_orig = int(re.match(r'idx(\d+).csv', file)[1])
    d = pd.read_csv(f'{path}/{file}')
    # drop first row
    d = d.iloc[1:]
    data_num_timesteps = len(d)
    if data_num_timesteps != 0:
        termination_list.append(d)
termination_df = pd.concat(termination_list)

## now we compute node attributes
import networkx as nx 

G = nx.from_pandas_edgelist(termination_df,
                            source = 'config_from',
                            target = 'config_to',
                            edge_attr = 'weight',
                            create_using = nx.DiGraph)

# need node attributes (e.g. log(p(config)))
# and whether they are termination states 
config_from = termination_df['config_from'].unique().tolist()
config_to = termination_df['config_to'].unique().tolist()
config_uniq = list(set(config_from + config_to))

# find probability of each of these
n_nodes = 20
configurations = np.loadtxt('..../data/preprocessing/configurations.txt')
configuration_probabilities = np.loadtxt('..../data/preprocessing/configuration_probabilities.txt')
p = configuration_probabilities[config_uniq]
import configuration as cn     
configs_probs = []
for config in config_uniq: 
    ConfObjx = cn.Configuration(config,
                                configurations,
                                configuration_probabilities)
    probx = ConfObjx.p 
    configs_probs.append((config, probx))


#### first whether they are termination states ###
unique_configs = pd.DataFrame(configs_probs, columns = ['config_id', 'config_prob'])

termination_states = termination_final[['config_id']].drop_duplicates()
termination_states['termination'] = 'tab:blue'
termination_status = unique_configs.merge(termination_states, 
                                          on = 'config_id', 
                                          how = 'left').fillna('tab:red')

#### then the weight of the configuration #####
# later we can do labels # 
#observed_state = entry_maxlikelihood[['config_id', 'entry_name']].drop_duplicates()
#observed_state # sample here 
#node_attr = termination_status.merge(entry_probability, on = 'config_id', how = 'left')

termination_status['log_config_prob'] = [np.log(x) for x in termination_status['config_prob']]

# add number pass 
passthrough_counts = termination_df['config_from'].append(termination_df.loc[termination_df['config_from'] != termination_df['config_to'], 
                                                                             'config_to']).value_counts().reset_index(name = 'passthrough')

passthrough_counts = passthrough_counts.rename(columns = {'index': 'config_id'})
termination_status = termination_status.merge(passthrough_counts, on = 'config_id', how = 'inner')

termination_status['log_pass'] = [np.log(x) for x in termination_status['passthrough']]


# add data to nodes 
for _, row in termination_status.iterrows(): 
    config_id = int(row['config_id'])
    G.nodes[config_id]['log_config_prob'] = row['log_config_prob']
    G.nodes[config_id]['config_prob'] = row['config_prob']
    G.nodes[config_id]['node_color'] = row['termination']
    G.nodes[config_id]['passthrough'] = row['passthrough']
    G.nodes[config_id]['log_pass'] = row['log_pass']

G.nodes(data=True)

pos = {}  
nodelist = []
node_color = []              
for node, attr in G.nodes(data = True): 
    pos[node] = np.array([attr['log_pass'], attr['log_config_prob']]) 
    nodelist.append(node)
    node_color.append(attr['node_color'])
    #node_size.append(number_pass)
    
# plot 
import matplotlib.pyplot as plt 
plt.figure(dpi = 300)
plt.axis('off')
nx.draw_networkx_nodes(G, 
                    pos = pos, 
                    nodelist = nodelist,
                    node_color = node_color,
                    #node_size = [(x+1)*20 for x in node_size],
                    edgecolors = 'k',
                    linewidths = 1,
                    node_size = 30)
nx.draw_networkx_edges(G, 
                    pos = pos,
                    edge_color = 'grey'
                    #edgelist = edgelist_sorted,
                    #edge_color = edge_color,
                    #width = edge_width
                    )
plt.show();
#plt.savefig(f'../fig/attractor_plots/{source}_{config_orig}.pdf')
#plt.close()
