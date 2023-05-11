'''
VMP 2023-05-08: 
Checking the raw values for the big gods data.
We will not be using this in the paper anyways. 
'''

import numpy as np 
import pandas as pd 

# load data 
d = pd.read_csv('../data/preprocessing/data_flattened.csv')
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')

# find the questions we care about 
monitor_idx = question_reference[question_reference['question'].str.contains('monitor')]['question_id_drh'].values[0]
punish_idx = question_reference[question_reference['question'].str.contains('punish')]['question_id_drh'].values[0]
polsup_idx = question_reference[question_reference['question'].str.contains('political')]['question_id_drh'].values[0]


## first the main effect ##
# subset the data
monitor_punish = [monitor_idx, punish_idx]
monitor_punish = [str(x) for x in monitor_punish]
d_m_p = d[monitor_punish]

# remove zeros 
d_m_p = d_m_p[(d_m_p != 0).all(axis=1)]
d_m_p_count = d_m_p.groupby([f'{monitor_idx}', f'{punish_idx}']).size().reset_index(name = 'count')
d_m_p_fraction = d_m_p_count.assign(fraction = lambda x: x['count']/x['count'].sum())
d_m_p_fraction # so very different from what we show in the paper (how did we calculate that?)

'''
0.730 / 0.064
0.061 / 0.145

vs

0.427 / 0.089
0.083 / 0.400
'''

## now marginalize over political support ## 
monitor_punish_polsup = [monitor_idx, punish_idx, polsup_idx]
monitor_punish_polsup = [str(x) for x in monitor_punish_polsup]
d_m_p_ps = d[monitor_punish_polsup]

# remove zeros
d_m_p_ps = d_m_p_ps[(d_m_p_ps != 0).all(axis=1)]
d_m_p_ps = d_m_p_ps[d_m_p_ps[f"{polsup_idx}"] == 1]
d_m_p_ps_count = d_m_p_ps.groupby([f'{monitor_idx}', f'{punish_idx}']).size().reset_index(name = 'count')
d_m_p_ps_fraction = d_m_p_ps_count.assign(fraction = lambda x: x['count']/x['count'].sum())
d_m_p_ps_fraction

'''
0.794 / 0.025
0.065 / 0.116

vs. 

0.404 / 0.052 
0.122 / 0.433
'''

# check whether what Simon did was just grab
# the raw probabilities, or something more sophisticated 
p_config = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')
config = np.loadtxt('../data/preprocessing/configurations.txt', dtype = int)

# get the 
monitor_idx = question_reference[question_reference['question_id_drh'] == monitor_idx]['question_id'].values[0] - 1
punish_idx = question_reference[question_reference['question_id_drh'] == punish_idx]['question_id'].values[0] - 1

idx_monitor_on_punish_on = np.where((config[:, monitor_idx] == 1) & (config[:, punish_idx] == 1))[0]
idx_monitor_on_punish_off = np.where((config[:, monitor_idx] == 1) & (config[:, punish_idx] == -1))[0]
idx_monitor_off_punish_on = np.where((config[:, monitor_idx] == -1) & (config[:, punish_idx] == 1))[0]
idx_monitor_off_punish_off = np.where((config[:, monitor_idx] == -1) & (config[:, punish_idx] == -1))[0]

p_config[idx_monitor_on_punish_on].sum() # 0.643
p_config[idx_monitor_on_punish_off].sum() # 0.070
p_config[idx_monitor_off_punish_on].sum() # 0.082
p_config[idx_monitor_off_punish_off].sum() # 0.204

# so these probabilities are not the same as we report in the paper
# question is what we actually do in the paper
# we should (at least) communicate that more clearly. 

# did we do the thing where for each combination of other attributes
# we look at the probability of the other features
# which means that we consider all parts of the landscape equally 
# meaningful (rather than the absolute case) ?

# this could make sense, but then we should explain why this is reasonable
# and perhaps include the absolute case as well. 
from tqdm import tqdm 
def relative_probabilities(configurations, 
                           configuration_probabilities,
                           idx_init, 
                           samples, 
                           sample_config_idx = False): 

    # reproducibility
    np.random.seed(seed = 1)
    # configurations ignoring two indices (i.e. 2**18 rather than 2**20)
    restricted_configurations = np.delete(configurations, [idx_init, idx_init + 1], 1)
    restricted_configurations = np.unique(restricted_configurations, axis = 0)
    n_configurations = len(restricted_configurations)
    if not sample_config_idx: 
        sample_config_idx = np.random.choice(n_configurations,
                                             size = samples,
                                             replace = False)
    sample_configs = restricted_configurations[[sample_config_idx]]

    # loop over the sample and calculate
    p_global = []
    for num, x in tqdm(enumerate(sample_configs)): 
        # get the configurations 
        conf_both = np.insert(x, idx_init, [1, 1])
        conf_first = np.insert(x, idx_init, [1, -1])
        conf_second = np.insert(x, idx_init, [-1, 1])
        conf_none = np.insert(x, idx_init, [-1, -1])
        # get the configuration idx 
        idx_both = np.where(np.all(configurations == conf_both, axis = 1))[0][0]
        idx_first = np.where(np.all(configurations == conf_first, axis = 1))[0][0]
        idx_second = np.where(np.all(configurations == conf_second, axis = 1))[0][0]
        idx_none = np.where(np.all(configurations == conf_none, axis = 1))[0][0]
        # get probabilities
        p_both = configuration_probabilities[idx_both]
        p_first = configuration_probabilities[idx_first]
        p_second = configuration_probabilities[idx_second]
        p_none = configuration_probabilities[idx_none]
        # gather in list 
        probabilities = (p_both, p_first, p_second, p_none)
        # put this together
        p_global.append(probabilities)

    return p_global

idx_first = 11 # monitoring
n_samples = 1000

p_list = relative_probabilities(config, p_config, idx_first, n_samples) 
d = pd.DataFrame(p_list, columns = ['both', 'first', 'second', 'none'])
d_norm = d.div(d.sum(axis = 1), axis = 0)
d_norm.mean() # much closer to what we actually report in the paper 

'''
0.441 / 0.081
0.090 / 0.388
'''