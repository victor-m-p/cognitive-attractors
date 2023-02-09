'''
Supplementary information plots.
VMP 2023-02-08: light refactoring, should be cleaned more (has been re-run)
'''

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import configuration as cn
from tqdm import tqdm 

# preprocessing 
configuration_probabilities = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')
configurations = np.loadtxt('../data/preprocessing/configurations.txt', dtype = int)

# find probability for different attributes
probability_list = []
for i in range(20): 
    column_n = configurations[:, i]
    column_n_idx = np.where(column_n > 0)
    column_probs = configuration_probabilities[column_n_idx]
    mean_prob = np.mean(column_probs)
    std_prob = np.std(column_probs)
    probability_list.append((i+1, mean_prob, std_prob))
probability_df = pd.DataFrame(probability_list, columns = ['question_id', 'mean(prob)', 'std(prob)'])

# match with questions 
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')
question_reference = question_reference[['question_id', 'question']]
question_probability = question_reference.merge(probability_df, on = 'question_id', how = 'inner')
question_probability = question_probability.sort_values('mean(prob)').reset_index()

global_mean = np.mean(configuration_probabilities)

fig, ax = plt.subplots(dpi = 300, figsize = (4, 6))
for i, row in question_probability.iterrows(): 
    x = row['mean(prob)']
    x_err = row['std(prob)']
    plt.scatter(x, i, color = 'tab:blue')
plt.yticks(np.arange(0, 20, 1), 
           question_probability['question'].values,
           size = 15)
plt.vlines(global_mean, ymin = 0, ymax = 20, color = 'tab:red', ls = '--')
plt.xlabel('Mean probability')
plt.savefig('../fig/pdf/feature_stability.pdf', bbox_inches = 'tight')
plt.savefig('../fig/svg/feature_stability.svg', bbox_inches = 'tight')

## look at standard deviation (much larger than actual difference?) ##
# ...

# most enforced practices
d_enforcement = pd.read_csv('../data/analysis/enforcement_observed.csv')
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')
observed_configs = d_enforcement['config_id'].unique().tolist()

# takes a couple of minutes
# not the most efficient approach
top_five_list = []
for config_idx in tqdm(observed_configs): 
    ConfObj = cn.Configuration(config_idx, 
                            configurations, 
                            configuration_probabilities)

    df = ConfObj.transition_probs_to_neighbors(question_reference)
    df = df.sort_values('transition_prob', ascending = False).head(5).reset_index()
    df = df[['question_id', 'question']]
    df['config_id'] = config_idx 
    top_five_list.append(df)

top_five_df = pd.concat(top_five_list)
top_five_df = top_five_df.groupby('question').size().reset_index(name = 'count')
top_five_df = top_five_df.sort_values('count', ascending = True).reset_index()

# plot this 
fig, ax = plt.subplots(dpi = 300, figsize = (4, 6))
for i, row in top_five_df.iterrows(): 
    x = row['count']
    plt.scatter(x, i, color = 'tab:blue')
plt.yticks(np.arange(0, 20, 1), 
           top_five_df['question'].values, 
           size = 15)
plt.xlabel('n(enforced first five)')
plt.savefig('../fig/pdf/number_enforced_first_five.pdf', bbox_inches = 'tight')
plt.savefig('../fig/svg/number_enforced_first_five.svg', bbox_inches = 'tight')

top_five_df = top_five_df.assign(percent_top_five = lambda x: (x['count']/260)*100)
top_five_df.sort_values('count', ascending = False)

# tables
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')

'''
### sacrifice ###
adult = configurations[:, 14]
child = configurations[:, 15]

adult_on = np.where(adult == 1)
adult_off = np.where(adult == -1)
child_on = np.where(child == 1)
child_off = np.where(child == -1)

## get the four quadrants
both_on = np.intersect1d(adult_on, child_on)
both_off = np.intersect1d(adult_off, child_off)
child_only = np.intersect1d(adult_off, child_on)
adult_only = np.intersect1d(adult_on, child_off)

## get probabilities
p_both_on = configuration_probabilities[both_on].mean()
p_both_off = configuration_probabilities[both_off].mean()
p_child_only = configuration_probabilities[child_only].mean()
p_adult_only = configuration_probabilities[adult_only].mean()

### big gods ###
monitor = configurations[:, 11]
punish = configurations[:, 12]

monitor_on = np.where(monitor == 1) 
monitor_off = np.where(monitor == -1)
punish_on = np.where(punish == 1)
punish_off = np.where(punish == -1)

## get the four quadrants 
both_on = np.intersect1d(monitor_on, punish_on)
both_off = np.intersect1d(monitor_off, punish_off)
monitor_only = np.intersect1d(monitor_on, punish_off)
punish_only = np.intersect1d(monitor_off, punish_on)

## get probabilities
p_both_on = configuration_probabilities[both_on].mean()
p_both_off = configuration_probabilities[both_off].mean()
p_monitor_only = configuration_probabilities[monitor_only].mean()
p_punish_only = configuration_probabilities[punish_only].mean()

p_both_on
p_both_off
p_monitor_only
p_punish_only
'''


# temp
reincarnation_top = top_five_df[top_five_df['question'] == 'Reincarnation in this world']

# temporary #
import pandas as pd 
import numpy as np 
import configuration as cn 
from tqdm import tqdm 

# load documents
entry_maxlikelihood = pd.read_csv('..../data/preprocessing/entry_maxlikelihood.csv')
configuration_probabilities = np.loadtxt('..../data/preprocessing/configuration_probabilities.txt')
question_reference = pd.read_csv('..../data/preprocessing/question_reference.csv')

# generate all states
n_nodes = 20
from fun import bin_states 
configurations = bin_states(n_nodes) 

# test something 
q_list = []
for configuration in reincarnation_top['config_id'].unique():
    conf = cn.Configuration(configuration,
                            configurations, 
                            configuration_probabilities)
    p_move = conf.configuration
    question_temp = question_reference
    question_temp['held_belief'] = conf.configuration
    question_temp = question_temp[question_temp['question'] == 'Reincarnation in this world']
    q_list.append(question_temp)

tst = pd.concat(q_list)
tst.groupby('held_belief').size()