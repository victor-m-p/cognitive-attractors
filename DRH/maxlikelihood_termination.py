import pandas as pd 
import numpy as np 
import os 
import re

path = '../data/COGSCI23/max_attractor'
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
entry_maxlikelihood = pd.read_csv('../data/analysis/entry_maxlikelihood.csv')
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

