# VMP 2023-02-08: refactored and re-run
import pandas as pd 
import numpy as np 
import configuration as cn 
from tqdm import tqdm 

# load documents
entry_maxlikelihood = pd.read_csv('../data/preprocessing/entry_maxlikelihood.csv')
configuration_probabilities = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')
configurations = np.loadtxt('../data/preprocessing/configurations.txt', dtype = int)
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')

# get all unique configurations 
unique_configurations = entry_maxlikelihood['config_id'].unique().tolist()

# around 2 minutes on local computer 
transition_list = []
for configuration in tqdm(unique_configurations): 
    conf = cn.Configuration(configuration,
                            configurations, 
                            configuration_probabilities)
    p_move = conf.p_move(summary = False)
    p_move = sorted(p_move, reverse = True)
    for n_fixed in range(20): 
        p_move_n = p_move[n_fixed:]
        p_mean_n = np.mean(p_move_n)
        transition_list.append((configuration, n_fixed, p_mean_n))

# save this 
d = pd.DataFrame(transition_list, columns = ['config_id', 'n_fixed_traits', 'prob_move'])
d.to_csv('../data/analysis/enforcement_observed.csv', index = False)