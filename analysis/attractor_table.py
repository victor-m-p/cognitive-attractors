'''
VMP 2023-05-09:
The table for attractor states (analytical)
'''

import pandas as pd 
import numpy as np 
import os 
import re

path = '../data/analysis/max_attractor' # from analytical max 
files = os.listdir(path)

# only consider end attractor
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

# gather in dataframe
termination_df = pd.DataFrame(termination_list,
                              columns = ['initial', 'attractor'])        

# aggregate by size 
termination_sum = termination_df.groupby('attractor').size().reset_index(name = 'count')
termination_sum = termination_sum.sort_values('count', ascending = False)
termination_sum = termination_sum.rename(columns = {'attractor': 'config_id'})

# add (global) probability 
p = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')
termination_sum['config_prob'] = p[termination_sum['config_id']]

# get all maximum likelihood configurations in here
entry_maxlikelihood = pd.read_csv('../data/preprocessing/entry_maxlikelihood.csv')
entry_maxlikelihood = entry_maxlikelihood[['config_id', 'entry_name']].drop_duplicates()
termination_entries = termination_sum.merge(entry_maxlikelihood, on = 'config_id', how = 'left', indicator=True).fillna('Unobserved')
termination_list = termination_entries.groupby('config_id')['entry_name'].apply(lambda x: " & ".join(x)).reset_index(name = 'entries')

# wrangle this to final format
termination_probs = termination_entries[['config_id', 'config_prob', 'count']].drop_duplicates()
termination_final = termination_list.merge(termination_probs, on = 'config_id', how = 'inner')
termination_final = termination_final[['config_id', 'config_prob', 'count', 'entries']]
termination_final = termination_final.sort_values('count', ascending=False)

# to latex 
pd.set_option('display.max_colwidth', None)
termination_latex = termination_final.to_latex(index=False)
with open('../tables/termination_states_260.txt', 'w') as f: 
    f.write(termination_latex)
